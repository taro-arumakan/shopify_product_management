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
        "manual_jan_codes": [str, ...],  # typed from the tag when unreadable
        "styling_photo_ids": [str, ...],   # Drive file ids, first is the cover
        "tag_photo_ids": [str, ...],       # Drive file ids of price-tag photos
        "spreadsheet_id": str
      }
    }

Steps:

1. skip the whole run if custom.styling_submission_id already carries this
   response id — a re-run must not leave the operator a second draft
2. download price-tag photos from Drive (the form's File responses folders are
   shared with the service account) and decode barcodes with zxing-cpp
3. resolve variants by the barcode field — JAN != SKU for ASHEIS; barcodes are
   populated from the products sheet's JANコード column by AsheisClient —
   falling back to SKU lookup so a manually typed code may be either
4. download styling photos, EXIF-orient, convert to JPEG (HEIC included) and
   cap resolution, then upload to Shopify Files
5. create the article hidden in the Styling blog ("styling" template) with the
   custom.styling_* metafields in the same mutation, author = staff name,
   tag = display name, title = display name + auto-increment
6. email the outcome to NOTIFYEES_STAFF_STYLING

The article is always created, even when no product could be identified or no
photo came through: a hidden draft plus a 要確認 email naming what is missing
lets the operator finish the article in the admin and publish it, which beats
a submission that leaves nothing behind. Only an unexpected error aborts, and
that too is emailed.
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
from helpers.exceptions import (
    MultipleVariantsFoundException,
    NoVariantsFoundException,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pillow_heif.register_heif_opener()

BLOG_TITLE = "Styling"
TEMPLATE_SUFFIX = "styling"
METAFIELD_NAMESPACE = "custom"
MAX_MEGAPIXELS = 15


def notifyees():
    """Recipients of the outcome mail, from NOTIFYEES_STAFF_STYLING.

    No default on purpose: this repository is public, so the addresses live in
    the GitHub secret and nowhere in the source.
    """
    raw = os.environ["NOTIFYEES_STAFF_STYLING"]
    addrs = [a.strip() for a in raw.split(",") if a.strip()]
    if not addrs:
        raise RuntimeError(
            "NOTIFYEES_STAFF_STYLING is empty — set the repository secret, "
            "or nobody is told what happened to a submission."
        )
    return addrs


def parse_submission():
    payload = json.loads(os.environ["CLIENT_PAYLOAD"])
    submission = payload["submission"]
    for key in ("staff", "styling_photo_ids", "tag_photo_ids"):
        assert key in submission, f"missing key in submission: {key}"
    # Optional fields, defaulted so a hand-fired dispatch payload still runs.
    submission.setdefault("manual_jan_codes", [])
    submission.setdefault("caption", "")
    submission.setdefault("response_id", "")
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
    """Resolve decoded barcodes / manually entered codes to variants.

    Decoded JANs match the variant barcode field; manual input may be either a
    JAN or a SKU, so barcode lookup is tried first, then SKU, raw code first
    and digits-only second. Returns (resolved variants, unresolved codes),
    variants deduped by id.
    """
    resolved, unresolved = [], []
    for code in codes:
        candidates = [code]
        digits = re.sub(r"\D", "", code)
        if digits and digits != code:
            candidates.append(digits)
        variant = None
        for candidate in candidates:
            for lookup in (client.variant_by_barcode, client.variant_by_sku):
                try:
                    variant = lookup(candidate)
                    break
                except (NoVariantsFoundException, MultipleVariantsFoundException):
                    # Anything else — a bad token, a rate limit — is a systemic
                    # failure and must not be reported as "code not found".
                    continue
            if variant:
                break
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


def blog_articles(client):
    """Every article in the blog, with the submission marker each carries.

    One paginated fetch serves both the numbering and the re-run check, and
    scanning locally keeps a staff display name out of the search query, where
    an unexpected character would silently match nothing.
    """
    query = """
    query articlesByQuery($query_string: String!, $after: String, $first: Int!) {
        articles(first: $first, query: $query_string, after: $after) {
            pageInfo {
                hasNextPage
                endCursor
            }
            nodes {
                id
                title
                submissionId: metafield(
                    namespace: "custom"
                    key: "styling_submission_id"
                ) {
                    value
                }
            }
        }
    }
    """
    return client.run_paginated_query(
        query, {"query_string": f"blog_title:'{BLOG_TITLE}'"}, "articles"
    )


def next_article_title(articles, display_name):
    """<display name><n>, one past the highest n already in the blog."""
    # Case-insensitively: the blog holds both "Miki17" and "MIKI18", and a
    # case-sensitive match would hand out a number that is already taken.
    pattern = re.compile(rf"^{re.escape(display_name)}(\d+)$", re.IGNORECASE)
    numbers = [
        int(m.group(1)) for a in articles if (m := pattern.match(a["title"] or ""))
    ]
    return f"{display_name}{max(numbers, default=0) + 1}"


def existing_article_for_submission(articles, response_id):
    """The article a previous run already created for this submission, if any.

    A re-run of the Action, or a response processed twice, would otherwise
    leave a second draft for the operator to notice and clean up.
    """
    if not response_id:
        return None
    for article in articles:
        marker = article.get("submissionId")
        if marker and marker["value"] == response_id:
            return article
    return None


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


def build_metafields(staff, variant_ids, file_ids, caption, response_id=""):
    # metafieldsSet and articleCreate both reject the whole batch on one bad
    # entry, so blank and empty values are omitted rather than sent: the
    # operator then sees a blank field to fill in and the template renders
    # nothing, instead of the article losing every metafield.
    entries = [("styling_model_name", "single_line_text_field", staff["display_name"])]
    if staff.get("height"):
        entries.append(
            ("styling_model_height", "single_line_text_field", staff["height"])
        )
    if response_id:
        # Idempotency key: what a re-run matches on to avoid a second article.
        entries.append(("styling_submission_id", "single_line_text_field", response_id))
    if file_ids:
        entries.append(
            ("styling_main_images", "list.file_reference", json.dumps(file_ids))
        )
    if variant_ids:
        entries.append(
            (
                "styling_product_variants",
                "list.variant_reference",
                json.dumps(variant_ids),
            )
        )
    if staff.get("instagram"):
        account = staff["instagram"].lstrip("@")
        entries.append(
            (
                "styling_model_instagram_link",
                "url",
                f"https://www.instagram.com/{account}/",
            )
        )
    if caption and caption.strip():
        entries.append(
            ("styling_caption", "rich_text_field", caption_rich_text(caption))
        )
    return [
        {"namespace": METAFIELD_NAMESPACE, "key": key, "type": type_, "value": value}
        for key, type_, value in entries
    ]


def admin_article_url(article_gid):
    return f"https://admin.shopify.com/store/asheis/content/articles/{article_gid.rsplit('/', 1)[-1]}"


def drive_file_url(file_id):
    return f"https://drive.google.com/file/d/{file_id}/view"


def spreadsheet_url(spreadsheet_id):
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"


def workflow_run_url():
    """Link to the Action run, from the variables GitHub injects into the job."""
    server = os.environ.get("GITHUB_SERVER_URL")
    repository = os.environ.get("GITHUB_REPOSITORY")
    run_id = os.environ.get("GITHUB_RUN_ID")
    if not (server and repository and run_id):
        return ""
    return f"{server}/{repository}/actions/runs/{run_id}"


def notify(subject, lines):
    body = "\n".join(lines)
    logger.info("notifying %s: %s\n%s", ", ".join(notifyees()), subject, body)
    send_smtp_email(subject, body, notifyees())


def identify_variants(client, submission, workdir):
    """Decode the tag photos and resolve them, and any manual entry, to variants.

    Returns (resolved variants, unresolved codes, ids of unreadable tag photos)
    — the ids, not a count, so the email can link the photo that needs a human.
    """
    unreadable, codes = [], []
    for i, file_id in enumerate(submission["tag_photo_ids"]):
        path = str(workdir / f"tag_{i}")
        try:
            client.download_file_from_drive(file_id, path)
            decoded = decode_barcodes(path)
        except Exception:
            # A photo PIL cannot open counts as unreadable, like one whose
            # barcode will not decode — it must not cost the whole article.
            logger.exception("could not read tag photo %s", file_id)
            decoded = []
        if decoded:
            codes.extend(decoded)
        else:
            unreadable.append(file_id)
    codes.extend(submission["manual_jan_codes"])
    resolved, unresolved = resolve_variants(client, list(dict.fromkeys(codes)))
    logger.info(
        "variants resolved: %s, unresolved codes: %s, unreadable tag photos: %s",
        [v["sku"] for v in resolved],
        unresolved,
        unreadable,
    )
    return resolved, unresolved, unreadable


def upload_styling_photos(client, submission, workdir, title):
    """Normalise the styling photos and upload them.

    Returns (file ids, cover url, ids of photos that could not be processed).
    One unreadable photo costs that photo, not the whole article.
    """
    local_paths, failed = [], []
    for i, file_id in enumerate(submission["styling_photo_ids"]):
        raw = str(workdir / f"styling_{i}_raw")
        try:
            client.download_file_from_drive(file_id, raw)
            local_paths.append(
                prepare_image(raw, str(workdir / f"{title.lower()}-{i + 1}.jpg"))
            )
        except Exception:
            logger.exception("could not process styling photo %s", file_id)
            failed.append(file_id)
    if not local_paths:
        return [], None, failed

    file_names = [pathlib.Path(p).name for p in local_paths]
    mime_types = ["image/jpeg"] * len(local_paths)
    staged_targets = client.generate_staged_upload_targets(file_names, mime_types)
    client.upload_images_to_shopify(staged_targets, local_paths, mime_types)
    files = client.create_files_from_staged_targets(
        [target["resourceUrl"] for target in staged_targets], alts=file_names
    )
    file_ids = [f["id"] for f in files]
    urls_by_id = client.wait_for_file_processing_completion(file_ids)
    return file_ids, urls_by_id[file_ids[0]], failed


def collect_warnings(report):
    """What the operator has to complete by hand before publishing."""
    warnings = []
    if report["failed_photos"]:
        warnings.append(
            f"・スタイリング写真を{len(report['failed_photos'])}枚取り込めませんでした。"
            "管理画面で追加してください"
        )
    if report["unreadable_tags"]:
        warnings.append(
            f"・下げ札写真を{len(report['unreadable_tags'])}枚読み取れませんでした"
        )
    if report["unresolved"]:
        warnings.append(
            f"・商品を特定できないコードがあります: {', '.join(report['unresolved'])}"
        )
    if report["unresolved"] or report["unreadable_tags"] or not report["resolved"]:
        # Fires on a partial match too: one unidentified item still needs the
        # operator to open the same metafield and add it.
        warnings.append(
            "・管理画面の「Styling - Product Variants」に"
            "着用商品を手動で追加してください"
        )
    if not report["uploaded_photos"]:
        # Keyed off what actually reached Shopify, not off what was submitted:
        # every photo failing to import leaves the article just as bare.
        warnings.append(
            "・スタイリング写真がありません。"
            "カバー画像と「Styling - Main Images」を手動で設定してください"
        )
    return warnings


def variant_line(variant):
    """Name the JAN as well: it is what is printed on the tag in the photo."""
    codes = f"SKU: {variant['sku']}"
    if variant.get("barcode"):
        codes += f" / JAN: {variant['barcode']}"
    return f"・{variant['displayName']} ({codes})"


def notify_outcome(submission, staff, title, article_id, report):
    warnings = report["warnings"]
    lines = [
        f"記事「{title}」を非公開で作成しました。"
        + (
            "下記の点を確認・修正のうえ公開してください。"
            if warnings
            else "内容を確認のうえ公開してください。"
        ),
        "",
        f"確認・公開: {admin_article_url(article_id)}",
        "",
        f"スタッフ: {staff['name']} ({staff['display_name']} / {staff['shop']})"
        + ("  ※新規登録" if staff.get("is_new") else ""),
        f"投稿者: {submission.get('respondent_email') or '(不明)'}",
        f"スタイリング写真: {report['uploaded_photos']}枚",
        "着用商品:" if report["resolved"] else "着用商品: 未特定",
        *[variant_line(v) for v in report["resolved"]],
    ]
    if warnings:
        lines += ["", "要確認:", *warnings]
        # The operator reads the tags themselves to identify what is missing,
        # so link them whenever identification came up short — but not when the
        # only problem was, say, a photo that failed to import.
        if submission["tag_photo_ids"] and (
            report["unresolved"] or report["unreadable_tags"] or not report["resolved"]
        ):
            lines += [
                "",
                "下げ札写真:",
                *[f"・{drive_file_url(i)}" for i in submission["tag_photo_ids"]],
            ]
        if report["failed_photos"]:
            lines += [
                "",
                "取り込めなかったスタイリング写真:",
                *[f"・{drive_file_url(i)}" for i in report["failed_photos"]],
            ]
        if spreadsheet_id := submission.get("spreadsheet_id"):
            lines += ["", f"回答内容: {spreadsheet_url(spreadsheet_id)}"]
    state = "要確認" if warnings else "完了"
    notify(f"【スタイリング投稿】{state}: {title} ({staff['name']})", lines)


def process_submission(submission, context):
    staff = submission["staff"]
    client = utils.client("asheis")
    workdir = pathlib.Path(tempfile.mkdtemp(prefix="staff_styling_"))

    articles = blog_articles(client)
    if existing := existing_article_for_submission(
        articles, submission.get("response_id")
    ):
        logger.info(
            "submission %s already produced %s, skipping",
            submission["response_id"],
            existing["title"],
        )
        notify(
            f"【スタイリング投稿】作成済み: {existing['title']} ({staff['name']})",
            [
                f"この投稿は既に記事「{existing['title']}」として作成済みのため、"
                "重複作成を避けて処理をスキップしました。",
                "",
                f"確認・公開: {admin_article_url(existing['id'])}",
                "",
                "その記事がまだ公開されていない場合は、内容を確認のうえ公開してください。",
            ],
        )
        return

    resolved, unresolved, unreadable_tags = identify_variants(
        client, submission, workdir
    )

    title = next_article_title(articles, staff["display_name"])
    file_ids, cover_url, failed_photos = upload_styling_photos(
        client, submission, workdir, title
    )
    report = {
        "resolved": resolved,
        "unresolved": unresolved,
        "unreadable_tags": unreadable_tags,
        "failed_photos": failed_photos,
        "uploaded_photos": len(file_ids),
    }
    report["warnings"] = collect_warnings(report)

    article = client.article_create(
        BLOG_TITLE,
        title,
        TEMPLATE_SUFFIX,
        media_url=cover_url,
        is_published=False,
        author_name=staff["name"],
        tags=[staff["display_name"]],
        metafields=build_metafields(
            staff,
            [v["id"] for v in resolved],
            file_ids,
            submission["caption"],
            submission.get("response_id", ""),
        ),
    )
    context["article_id"] = article["id"]
    logger.info("created article %s: %s", article["title"], article["id"])

    notify_outcome(submission, staff, title, article["id"], report)


def notify_error(staff, context, exc):
    lines = [
        "スタイリング記事の作成処理でエラーが発生しました。",
        "",
        f"エラー: {type(exc).__name__}: {exc}",
    ]
    if article_id := context.get("article_id"):
        lines += ["", f"作成途中の記事: {admin_article_url(article_id)}"]
    lines += [
        "",
        f"実行ログ: {workflow_run_url() or 'GitHub Actions を確認してください'}",
    ]
    try:
        notify(f"【スタイリング投稿】エラー: {staff.get('name', '')}", lines)
    except Exception:  # the original error matters more than the notification
        logger.exception("failed to send the error notification")


def main():
    # Parsing is inside the try as well: a malformed payload is exactly the
    # case nobody is watching the Action for, so it has to reach the mailbox.
    context, staff = {}, {}
    try:
        notifyees()  # fail before the work, not after, if it is unconfigured
        submission = parse_submission()
        staff = submission["staff"]
        logger.info(
            "processing %s by %s (%s)",
            submission.get("response_id"),
            staff.get("name"),
            staff.get("display_name"),
        )
        process_submission(submission, context)
    except Exception as exc:
        notify_error(staff, context, exc)
        raise


if __name__ == "__main__":
    main()
