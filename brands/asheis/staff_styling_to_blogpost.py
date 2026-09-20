"""Process a staff styling submission into a Styling blog article.

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
   response id — a re-run must not publish the same post twice
2. download price-tag photos from Drive (the form's File responses folders are
   shared with the service account) and decode barcodes with zxing-cpp
3. resolve variants by the barcode field — JAN != SKU for ASHEIS; barcodes are
   populated from the products sheet's JANコード column by AsheisClient —
   falling back to SKU lookup so a manually typed code may be either
4. download styling photos, EXIF-orient, convert to JPEG (HEIC included) and
   cap resolution, then upload to Shopify Files
5. create the article in the Styling blog ("styling" template) with the
   custom.styling_* metafields in the same mutation, author = staff name,
   tag = display name, title = display name + auto-increment — published
   straight away when it has at least one identified product and one photo,
   hidden otherwise
6. email the outcome to NOTIFYEES_STAFF_STYLING

The article is always created, even when no product could be identified or no
photo came through: a hidden draft plus a 要確認 email naming what is missing
lets the operator finish the article in the admin and publish it, which beats
a submission that leaves nothing behind. Past the publishing threshold a
problem no longer holds the article back — a second item whose tag would not
read still gets a 要確認 email, but the post is already live. Only an
unexpected error aborts, and that too is emailed.
"""

import json
import logging
import os
import pathlib
import re
import tempfile

import pillow_heif
import zxingcpp
from PIL import Image, ImageFilter, ImageOps

from dotenv import load_dotenv

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
# ASHEIS's GS1 company prefix. Every JAN the shops can scan starts with it.
JAN_PREFIX = "4550351"


def notifyees():
    """Recipients of the outcome mail, from NOTIFYEES_STAFF_STYLING.

    No default on purpose: this repository is public, so the addresses live in
    the GitHub secret and nowhere in the source.
    """
    # .get, not [] — the workflow writes the key into .env unconditionally, so
    # an unset secret arrives as an empty value rather than a missing one.
    raw = os.environ.get("NOTIFYEES_STAFF_STYLING", "")
    addrs = [a.strip() for a in raw.split(",") if a.strip()]
    if not addrs:
        raise RuntimeError(
            "NOTIFYEES_STAFF_STYLING is unset or empty — set the repository "
            "secret, or nobody is told what happened to a submission."
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


def unsharp_radius(width):
    """Sharpening radius for an image this wide.

    Blur is a fixed fraction of the tag, not a fixed number of pixels, so the
    radius that pulls the bar edges back at one scale is the wrong grain at
    another: it blurs detail away below that scale and does nothing above it.
    A tag that read at 1200px wide with radius 2 read at nothing else, and the
    ratio behind that holds across the tags we have.
    """
    return max(1, round(width / 550))


def sharpen(image, percent=200):
    return ImageOps.grayscale(image).filter(
        ImageFilter.UnsharpMask(radius=unsharp_radius(image.width), percent=percent)
    )


def decode_barcodes(image_path):
    """Every ASHEIS JAN readable from the image.

    A few downscales and a few small rotations: zxing straightens 90-degree
    orientation but not the handful of degrees of skew a hand-held photo has,
    and a tag shot at an angle can be unreadable flat yet read cleanly once
    tilted back. One real submission only read at all after a 6-12 degree
    rotation, and read wrongly without it.

    A decode outside the company prefix is dropped as a misread rather than
    reported as an unknown product. A blurred scan can return a different code
    that still passes the check digit — EAN-13 carries its first digit in the
    parity of the left-hand group, not in a bar, so a soft image can flip it
    and stay self-consistent. Sending the operator hunting for 0550355353233
    when the tag reads 4550351353233 helps nobody.
    """
    img = ImageOps.exif_transpose(Image.open(image_path))
    downscales = [
        img.resize((width, int(img.height * width / img.width)))
        for width in (2400, 1600, 1200)
        if img.width > width
    ]
    attempts = [img, *downscales, ImageOps.autocontrast(ImageOps.grayscale(img))]

    # Sharpening rescues the other common shop photo: a tag whose bars come out
    # pale and soft, under bright light or slightly out of focus, which reads as
    # no barcode at all until the edges are pulled back. Every rendition gets
    # its own, because the radius only works at the scale it was picked for —
    # see unsharp_radius.
    bases = [img, *downscales]
    sharpened = [sharpen(base) for base in bases]
    attempts += sharpened

    # Deskew from a downscale: full resolution is slow and no more readable.
    i = 1 if downscales else 0
    for angle in (6, -6, 12, -12):
        for rendition in (bases[i], sharpened[i]):
            attempts.append(
                rendition.rotate(
                    angle, expand=True, fillcolor="white", resample=Image.BICUBIC
                )
            )

    found, rejected = {}, {}
    for attempt in attempts:
        for result in zxingcpp.read_barcodes(attempt):
            if not result.text:
                continue
            target = found if result.text.startswith(JAN_PREFIX) else rejected
            target.setdefault(result.text, str(result.format))
    for text, fmt in found.items():
        logger.info("decoded %s: %s", fmt, text)
    for text in rejected:
        logger.warning("ignoring %s: not an ASHEIS JAN, so a misread", text)
    return list(found)


def resolve_variants(client, codes):
    """Resolve decoded barcodes / manually entered codes to variants.

    Decoded JANs match the variant barcode field; manual input may be either a
    JAN or a SKU, so barcode lookup is tried first, then SKU, raw code first
    and digits-only second. Returns (resolved variants deduped by id,
    unresolved codes, the variant each resolved code matched) — the last so a
    tag photo can be reported against what its own barcode found.
    """
    resolved, unresolved, matched = [], [], {}
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
            continue
        matched[code] = variant
        if variant["id"] not in [v["id"] for v in resolved]:
            resolved.append(variant)
    return resolved, unresolved, matched


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
    if staff.get("shop"):
        # Snapshotted, like the height and the Instagram handle: a post made
        # from one shop should keep naming that shop after the staff member
        # moves to another.
        entries.append(("styling_shop_name", "single_line_text_field", staff["shop"]))
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

    Returns (resolved variants, unresolved codes, one record per tag photo).
    Each record carries the photo's file id, the codes read off it, the
    variants they matched and the codes that matched nothing, so the email can
    say which photo needs a human and why rather than listing them all.
    """
    tags, codes = [], []
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
        tags.append({"file_id": file_id, "codes": decoded})
        codes.extend(decoded)
    codes.extend(submission["manual_jan_codes"])
    resolved, unresolved, matched = resolve_variants(client, list(dict.fromkeys(codes)))
    for tag in tags:
        tag["variants"] = [matched[c] for c in tag["codes"] if c in matched]
        tag["unresolved"] = [c for c in tag["codes"] if c not in matched]
    logger.info(
        "variants resolved: %s, unresolved codes: %s, unreadable tag photos: %s",
        [v["sku"] for v in resolved],
        unresolved,
        unreadable_tag_ids(tags),
    )
    return resolved, unresolved, tags


def unreadable_tag_ids(tags):
    return [t["file_id"] for t in tags if not t["codes"]]


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


# Below either of these the post would be a card with nothing to show or
# nothing to buy, so it stays hidden until the operator completes it.
PUBLISH_MIN_PRODUCTS = 1
PUBLISH_MIN_PHOTOS = 1


def should_publish(report):
    """Whether the article can go live without anyone looking at it first.

    Counts what actually reached Shopify, not what was submitted: five photos
    that all failed to import leave the article just as bare as none.
    """
    return (
        len(report["resolved"]) >= PUBLISH_MIN_PRODUCTS
        and report["uploaded_photos"] >= PUBLISH_MIN_PHOTOS
    )


def collect_warnings(report):
    """What the operator has to complete by hand in the admin."""
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


def tag_photo_lines(tags):
    """The tag photos, split into those that need a human and those that read.

    Empty when every tag read and matched: there is nothing to point at. When
    one did not, the ones that did are listed too, with what they matched, so
    whoever completes the post can see which items are already on it and does
    not re-check a photo that was fine.
    """
    needs_attention = [t for t in tags if not t["codes"] or t["unresolved"]]
    if not needs_attention:
        return []
    read = [t for t in tags if t not in needs_attention]

    def entry(tag):
        lines = [f"・{drive_file_url(tag['file_id'])}"]
        if not tag["codes"]:
            lines.append("  バーコードを読み取れませんでした")
        elif tag["unresolved"]:
            lines.append(f"  該当する商品がありません: {', '.join(tag['unresolved'])}")
        lines += [f"  {v['displayName']}" for v in tag["variants"]]
        return lines

    lines = ["", "要確認の下げ札写真:"]
    for tag in needs_attention:
        lines += entry(tag)
    if read:
        lines += ["", "読み取り済みの下げ札写真:"]
        for tag in read:
            lines += entry(tag)
    return lines


def outcome_mail(submission, staff, title, article_id, report):
    """Subject and body lines of the mail reporting a created article."""
    warnings = report["warnings"]
    if report["published"]:
        opening = f"記事「{title}」を公開しました。" + (
            "下記の点を確認し、必要に応じて管理画面で修正してください。"
            if warnings
            else ""
        )
        link_label = "確認・編集"
        state = "公開・要確認" if warnings else "公開"
    else:
        opening = (
            f"記事「{title}」を非公開で作成しました。"
            f"公開の条件(着用商品{PUBLISH_MIN_PRODUCTS}点以上・"
            f"スタイリング写真{PUBLISH_MIN_PHOTOS}枚以上)を満たさないため、"
            "下記の点を修正のうえ公開してください。"
        )
        link_label = "確認・公開"
        state = "非公開・要確認"
    lines = [
        opening,
        "",
        f"{link_label}: {admin_article_url(article_id)}",
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
        lines += tag_photo_lines(report["tags"])
        if report["failed_photos"]:
            lines += [
                "",
                "取り込めなかったスタイリング写真:",
                *[f"・{drive_file_url(i)}" for i in report["failed_photos"]],
            ]
        if spreadsheet_id := submission.get("spreadsheet_id"):
            lines += ["", f"回答内容: {spreadsheet_url(spreadsheet_id)}"]
    return f"【スタイリング投稿】{state}: {title} ({staff['name']})", lines


def notify_outcome(submission, staff, title, article_id, report):
    notify(*outcome_mail(submission, staff, title, article_id, report))


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

    resolved, unresolved, tags = identify_variants(client, submission, workdir)

    title = next_article_title(articles, staff["display_name"])
    file_ids, cover_url, failed_photos = upload_styling_photos(
        client, submission, workdir, title
    )
    report = {
        "resolved": resolved,
        "unresolved": unresolved,
        "tags": tags,
        "unreadable_tags": unreadable_tag_ids(tags),
        "failed_photos": failed_photos,
        "uploaded_photos": len(file_ids),
    }
    report["warnings"] = collect_warnings(report)
    report["published"] = should_publish(report)

    article = client.article_create(
        BLOG_TITLE,
        title,
        TEMPLATE_SUFFIX,
        media_url=cover_url,
        is_published=report["published"],
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
    logger.info(
        "created article %s (%s): %s",
        article["title"],
        "published" if report["published"] else "hidden",
        article["id"],
    )

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
    # The recipients live in .env, which nothing has read yet: utils.credentials
    # loads it, and that only happens once process_submission builds the client.
    # Load it here so the check below sees the configured value.
    assert load_dotenv(override=True)

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
