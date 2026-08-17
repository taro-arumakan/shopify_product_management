"""Process a staff styling submission into a hidden Styling blog article.

Triggered by .github/workflows/staff_styling_article.yml on a
``repository_dispatch`` event of type ``staff-styling-submission``, sent by the
Apps Script in brands/asheis/staff_styling/Code.gs. The payload arrives via the
CLIENT_PAYLOAD env var:

    {
      "submission": {
        "response_id": str,
        "submitted_at": str,          # ISO 8601
        "respondent_email": str,
        "staff": {"name": str, "display_name": str, "height": str,
                  "instagram": str, "shop": str, "is_new": bool},
        "caption": str,
        "manual_skus": [str, ...],    # fallback when tag photos are unusable
        "styling_photo_ids": [str, ...],   # Drive file ids, first is the cover
        "tag_photo_ids": [str, ...],       # Drive file ids of price-tag photos
        "spreadsheet_id": str
      }
    }

Steps:

1. download price-tag photos from Drive (the form's File responses folders are
   shared with the service account) and decode barcodes with zxing-cpp
2. resolve variants via variant_by_sku — JAN == SKU for ASHEIS — merging in
   manual_skus
3. download styling photos, EXIF-orient, convert to JPEG (HEIC included) and
   cap resolution, then upload to Shopify Files
4. create the article hidden in the Styling blog ("styling" template),
   author = staff name, tag = staff display name, title = display name +
   auto-increment, and set the custom.styling_* metafields
5. email the outcome to NOTIFYEES_STAFF_STYLING
"""

import json
import logging
import os
import pathlib
import re
import tempfile

import pillow_heif
import zxingcpp
from PIL import Image, ImageOps

import utils
from helpers.client import send_smtp_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pillow_heif.register_heif_opener()

BLOG_TITLE = "Styling"
TEMPLATE_SUFFIX = "styling"
METAFIELD_NAMESPACE = "custom"
DEFAULT_NOTIFYEES = (
    "yusuke@catal.co.jp,taro@sniarti.fi"  # TODO [CEC-470] remove default notifyees
)
MAX_MEGAPIXELS = 15
MIN_STYLING_PHOTOS = 4


def notifyees():
    addrs = os.environ.get("NOTIFYEES_STAFF_STYLING", DEFAULT_NOTIFYEES)
    return [a.strip() for a in addrs.split(",") if a.strip()]


def parse_submission():
    payload = json.loads(os.environ["CLIENT_PAYLOAD"])
    submission = payload["submission"]
    for key in ("staff", "styling_photo_ids", "tag_photo_ids"):
        assert key in submission, f"missing key in submission: {key}"
    return submission


def decode_barcodes(image_path):
    """Return every barcode value readable from the image."""
    img = ImageOps.exif_transpose(Image.open(image_path))
    attempts = [img]
    for width in (2400, 1600, 1200):
        if img.width > width:
            attempts.append(img.resize((width, int(img.height * width / img.width))))
    attempts.append(ImageOps.autocontrast(ImageOps.grayscale(img)))
    found = {}
    for attempt in attempts:
        for result in zxingcpp.read_barcodes(attempt):
            if result.text and result.text not in found:
                found[result.text] = str(result.format)
    for text, fmt in found.items():
        logger.info("decoded %s: %s", fmt, text)
    return list(found)


def resolve_variants(client, codes):
    """Resolve barcode values / manually entered SKUs to variants.

    Tries the raw code first, then a digits-only variant of it. Returns
    (resolved variants, unresolved codes), variants deduped by id.
    """
    resolved, unresolved = [], []
    for code in codes:
        candidates = [code]
        digits = re.sub(r"\D", "", code)
        if digits and digits != code:
            candidates.append(digits)
        variant = None
        for candidate in candidates:
            try:
                variant = client.variant_by_sku(candidate)
                break
            except Exception:
                continue
        if variant is None:
            unresolved.append(code)
        elif variant["id"] not in [v["id"] for v in resolved]:
            resolved.append(variant)
    return resolved, unresolved


def prepare_image(src_path, dst_path):
    """EXIF-orient, convert to JPEG (HEIC included) and cap the resolution."""
    with Image.open(src_path) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode != "RGB":
            img = img.convert("RGB")
        megapixels = img.width * img.height / 1_000_000
        if megapixels > MAX_MEGAPIXELS:
            scale = (MAX_MEGAPIXELS / megapixels) ** 0.5
            img = img.resize(
                (int(img.width * scale), int(img.height * scale)), Image.LANCZOS
            )
        img.save(dst_path, format="JPEG", quality=90)
    return dst_path


def next_article_title(client, display_name):
    query = """
    query articlesByQuery($query_string: String!) {
        articles(first: 250, query: $query_string) {
            nodes {
                title
            }
        }
    }
    """
    res = client.run_query(query, {"query_string": f"blog_title:'{BLOG_TITLE}'"})
    pattern = re.compile(rf"^{re.escape(display_name)}(\d+)$")
    numbers = [
        int(m.group(1))
        for node in res["articles"]["nodes"]
        if (m := pattern.match(node["title"]))
    ]
    return f"{display_name}{max(numbers, default=0) + 1}"


def caption_rich_text(caption):
    paragraphs = [line.strip() for line in caption.splitlines() if line.strip()]
    return json.dumps(
        {
            "type": "root",
            "children": [
                {"type": "paragraph", "children": [{"type": "text", "value": p}]}
                for p in paragraphs
            ],
        }
    )


def build_metafields(staff, variant_ids, file_ids, caption):
    entries = [
        ("styling_model_name", "single_line_text_field", staff["display_name"]),
        ("styling_model_height", "single_line_text_field", staff["height"]),
        ("styling_main_images", "list.file_reference", json.dumps(file_ids)),
        ("styling_product_variants", "list.variant_reference", json.dumps(variant_ids)),
    ]
    if staff.get("instagram"):
        account = staff["instagram"].lstrip("@")
        entries.append(
            (
                "styling_model_instagram_link",
                "url",
                f"https://www.instagram.com/{account}/",
            )
        )
    if caption:
        entries.append(
            ("styling_caption", "rich_text_field", caption_rich_text(caption))
        )
    return [
        {"namespace": METAFIELD_NAMESPACE, "key": key, "type": type_, "value": value}
        for key, type_, value in entries
    ]


def admin_article_url(article_gid):
    return f"https://admin.shopify.com/store/asheis/content/articles/{article_gid.rsplit('/', 1)[-1]}"


def notify(subject, lines):
    body = "\n".join(lines)
    logger.info("notifying %s: %s\n%s", ", ".join(notifyees()), subject, body)
    send_smtp_email(subject, body, notifyees())


def main():
    submission = parse_submission()
    staff = submission["staff"]
    logger.info(
        "processing %s by %s (%s)",
        submission.get("response_id"),
        staff["name"],
        staff["display_name"],
    )
    client = utils.client("asheis")
    workdir = pathlib.Path(tempfile.mkdtemp(prefix="staff_styling_"))

    undecodable = 0
    codes = []
    for i, file_id in enumerate(submission["tag_photo_ids"]):
        path = str(workdir / f"tag_{i}")
        client.download_file_from_drive(file_id, path)
        if decoded := decode_barcodes(path):
            codes.extend(decoded)
        else:
            undecodable += 1
    codes.extend(submission["manual_skus"])
    codes = list(dict.fromkeys(codes))
    resolved, unresolved = resolve_variants(client, codes)
    logger.info(
        "variants resolved: %s, unresolved codes: %s, undecodable tag photos: %s",
        [v["sku"] for v in resolved],
        unresolved,
        undecodable,
    )

    warnings = []
    if undecodable:
        warnings.append(
            f"・バーコードを読み取れない下げ札写真が{undecodable}枚ありました"
        )
    if unresolved:
        warnings.append(
            f"・商品を特定できないコードがありました: {', '.join(unresolved)}"
        )
    if len(submission["styling_photo_ids"]) < MIN_STYLING_PHOTOS:
        warnings.append(
            f"・スタイリング写真が{MIN_STYLING_PHOTOS}枚未満です"
            f"({len(submission['styling_photo_ids'])}枚)"
        )

    if not submission["styling_photo_ids"] or not resolved:
        reason = (
            "スタイリング写真がありません"
            if not submission["styling_photo_ids"]
            else "着用商品を1点も特定できませんでした"
        )
        notify(
            f"【スタイリング投稿】記事作成失敗: {staff['name']}",
            [
                f"記事を作成できませんでした: {reason}",
                "",
                *warnings,
                "",
                "フォームの回答内容を確認のうえ、SKU手入力での再投稿、または手動での記事作成をお願いします。",
            ],
        )
        raise SystemExit(f"article not created: {reason}")

    title = next_article_title(client, staff["display_name"])

    local_paths = []
    for i, file_id in enumerate(submission["styling_photo_ids"]):
        raw = str(workdir / f"styling_{i}_raw")
        client.download_file_from_drive(file_id, raw)
        local_paths.append(
            prepare_image(raw, str(workdir / f"{title.lower()}-{i + 1}.jpg"))
        )

    file_names = [pathlib.Path(p).name for p in local_paths]
    mime_types = ["image/jpeg"] * len(local_paths)
    staged_targets = client.generate_staged_upload_targets(file_names, mime_types)
    client.upload_images_to_shopify(staged_targets, local_paths, mime_types)
    files = client.create_files_from_staged_targets(
        [target["resourceUrl"] for target in staged_targets], alts=file_names
    )
    file_ids = [f["id"] for f in files]
    urls_by_id = client.wait_for_file_processing_completion(file_ids)

    article = client.article_create(
        BLOG_TITLE,
        title,
        TEMPLATE_SUFFIX,
        media_url=urls_by_id[file_ids[0]],
        is_published=False,
        author_name=staff["name"],
        tags=[staff["display_name"]],
    )
    logger.info("created article %s: %s", article["title"], article["id"])

    client.metafields_set(
        article["id"],
        build_metafields(
            staff, [v["id"] for v in resolved], file_ids, submission["caption"]
        ),
    )

    notify(
        f"【スタイリング投稿】記事作成完了: {title} ({staff['name']})",
        [
            f"記事「{title}」を非公開で作成しました。内容を確認のうえ公開してください。",
            "",
            f"確認・公開: {admin_article_url(article['id'])}",
            "",
            f"スタッフ: {staff['name']} ({staff['display_name']} / {staff['shop']})",
            f"スタイリング写真: {len(file_ids)}枚",
            "着用商品:",
            *[f"・{v['displayName']} (SKU: {v['sku']})" for v in resolved],
            *(["", *warnings] if warnings else []),
        ],
    )


if __name__ == "__main__":
    main()
