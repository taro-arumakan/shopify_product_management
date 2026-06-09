import argparse
import logging
import re

import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ROH の週次 Slideshow 画像のシーズン（キャンペーン）prefix。
# シーズンが変わったらここを更新する（例: "26_fall", "27_spring"）。
# ファイル名形式: {prefix}_pc_{N}w.jpg / {prefix}_m_{N}w.jpg
ROH_SEASON_PREFIX = "26_resort"

WEEK_IN_URL_RE = re.compile(r"(\d+)w\.(jpg|jpeg|png|webp)$", re.IGNORECASE)


def _weekly_url_patterns(season_prefix: str) -> tuple[re.Pattern[str], re.Pattern[str]]:
    escaped = re.escape(season_prefix)
    desktop = re.compile(
        rf"^shopify://shop_images/{escaped}_pc_(\d+)w\.(jpg|jpeg|png|webp)$",
        re.IGNORECASE,
    )
    mobile = re.compile(
        rf"^shopify://shop_images/{escaped}_m_(\d+)w\.(jpg|jpeg|png|webp)$",
        re.IGNORECASE,
    )
    return desktop, mobile


def _next_week(current_week: int, wrap_at: int | None) -> int:
    if wrap_at is None:
        return current_week + 1
    return 1 if current_week >= wrap_at else current_week + 1


def _match_weekly_urls(
    image_url: str, mobile_url: str, season_prefix: str
) -> int | None:
    desktop_re, mobile_re = _weekly_url_patterns(season_prefix)
    desktop_match = desktop_re.match(image_url or "")
    mobile_match = mobile_re.match(mobile_url or "")
    if not desktop_match or not mobile_match:
        return None
    week_image = int(desktop_match.group(1))
    week_mobile = int(mobile_match.group(1))
    if week_image != week_mobile:
        return None
    return week_image


def _filename_from_url(url: str) -> str:
    return url.removeprefix("shopify://shop_images/")


def _url_with_week(url: str, target_week: int) -> str:
    return WEEK_IN_URL_RE.sub(
        lambda m: f"{target_week}w.{m.group(2)}",
        url,
        count=1,
    )


def _shop_image_exists(client, filename: str) -> bool:
    stem = filename.rsplit(".", 1)[0]
    query = """
    query {
        files(first: 10, query: "filename:%s") {
            nodes {
                ... on MediaImage {
                    image {
                        url
                    }
                }
            }
        }
    }
    """ % (
        stem.replace('"', '\\"'),
    )
    res = client.run_query(query)
    for node in res["files"]["nodes"]:
        url = (node.get("image") or {}).get("url") or ""
        if url.rsplit("?", 1)[0].endswith(filename):
            return True
    return False


def _resolve_theme(client, theme_name: str | None):
    if theme_name:
        themes = client.themes_by_names(theme_name)
        if len(themes) != 1:
            raise RuntimeError(f"Theme not found or ambiguous: {theme_name!r}")
        return themes[0]
    theme = client.current_theme()
    if not theme:
        raise RuntimeError("No active theme found (role=MAIN).")
    return theme


def find_weekly_slideshow_blocks(
    data,
    section_type: str = "slideshow",
    season_prefix: str = ROH_SEASON_PREFIX,
) -> list[dict]:
    """設定したシーズン prefix に一致する Slideshow の Image ブロックを探す。"""
    blocks = []
    for section_id, section in data.get("sections", {}).items():
        if section.get("type") != section_type:
            continue
        for block_id, block in section.get("blocks", {}).items():
            if block.get("type") != "image":
                continue
            settings = block.get("settings", {})
            image_url = settings.get("image") or ""
            mobile_url = settings.get("mobile_image") or ""
            week = _match_weekly_urls(image_url, mobile_url, season_prefix)
            if week is None:
                continue
            blocks.append(
                {
                    "section_id": section_id,
                    "block_id": block_id,
                    "image_url": image_url,
                    "mobile_image_url": mobile_url,
                    "week": week,
                }
            )
    return blocks


def _inspect_weekly_images(
    client,
    theme,
    theme_file: str,
    content: str,
    section_type: str,
    season_prefix: str,
) -> None:
    data = client.theme_json_to_dict(content)
    blocks = find_weekly_slideshow_blocks(
        data, section_type=section_type, season_prefix=season_prefix
    )

    print(f"theme: {theme['name']} ({theme['id']}, role={theme['role']})")
    print(f"file: {theme_file}")
    print(f"section type: {section_type}")
    print(f"season prefix: {season_prefix}")
    print(f"weekly image blocks found: {len(blocks)}")
    print()

    for i, block in enumerate(blocks, start=1):
        print(f"[block {i}] section={block['section_id']} block={block['block_id']}")
        print(f"  week: {block['week']}")
        for label, url in [
            ("desktop", block["image_url"]),
            ("mobile", block["mobile_image_url"]),
        ]:
            filename = _filename_from_url(url)
            print(f"  {label}: {url}")
            print(f"    filename: {filename}")
            print(f"    in Shopify Files: {_shop_image_exists(client, filename)}")
        print()


def _apply_weekly_update(content: str, block: dict, target_week: int) -> str:
    new_desktop = _url_with_week(block["image_url"], target_week)
    new_mobile = _url_with_week(block["mobile_image_url"], target_week)

    if new_desktop == block["image_url"] and new_mobile == block["mobile_image_url"]:
        return content

    if block["image_url"] not in content:
        raise RuntimeError(f"Desktop URL not found in theme file: {block['image_url']}")
    if block["mobile_image_url"] not in content:
        raise RuntimeError(f"Mobile URL not found in theme file: {block['mobile_image_url']}")

    new_content = content.replace(block["image_url"], new_desktop, 1)
    if new_content.count(new_desktop) != 1:
        raise RuntimeError(f"Desktop URL replacement ambiguous: {new_desktop}")
    new_content = new_content.replace(block["mobile_image_url"], new_mobile, 1)
    if new_content.count(new_mobile) != 1:
        raise RuntimeError(f"Mobile URL replacement ambiguous: {new_mobile}")

    return new_content


def main():
    parser = argparse.ArgumentParser(
        description="ROH Seoul: トップ Slideshow の週次画像 URL を更新する。"
    )
    parser.add_argument("--shop-name", required=True, help="roh のみ（ROH Seoul 専用）")
    parser.add_argument(
        "--theme-name",
        default=None,
        help="Optional theme name. If omitted, uses the currently published theme (role=MAIN).",
    )
    parser.add_argument(
        "--theme-file",
        default="templates/index.json",
        help="Theme file path to update.",
    )
    parser.add_argument(
        "--section-type",
        default="slideshow",
        help="Section type to search for weekly image blocks (default: slideshow).",
    )
    parser.add_argument(
        "--target-week",
        type=int,
        default=None,
        help="If omitted, auto-increment from the detected block's current week.",
    )
    parser.add_argument(
        "--wrap-at",
        type=int,
        default=None,
        help="Optional loop upper bound. e.g. 8 means 8 -> 1.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print what would change without upserting.",
    )
    parser.add_argument(
        "--skip-if-missing-images",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Skip theme update when target-week images are not uploaded (default: on).",
    )
    parser.add_argument(
        "--inspect-only",
        action="store_true",
        help="Fetch and print current weekly slideshow image URLs only (no theme changes).",
    )
    args = parser.parse_args()

    client = utils.client(args.shop_name)
    theme = _resolve_theme(client, args.theme_name)
    logger.info("Target theme: %s (%s, role=%s)", theme["name"], theme["id"], theme["role"])

    file_nodes = client.theme_file_by_theme_name_and_file_name(
        theme["name"], args.theme_file
    )
    if not file_nodes:
        raise RuntimeError(f"Theme file not found: {args.theme_file}")
    current_content = file_nodes[0]["body"]["content"]
    data = client.theme_json_to_dict(current_content)
    blocks = find_weekly_slideshow_blocks(
        data, section_type=args.section_type, season_prefix=ROH_SEASON_PREFIX
    )
    logger.info("Season prefix: %s", ROH_SEASON_PREFIX)

    if args.inspect_only:
        _inspect_weekly_images(
            client,
            theme,
            args.theme_file,
            current_content,
            args.section_type,
            ROH_SEASON_PREFIX,
        )
        return

    if len(blocks) == 0:
        logger.info(
            "Skip update: no %s Image block with %s_* PC/SP images found.",
            args.section_type,
            ROH_SEASON_PREFIX,
        )
        return
    if len(blocks) > 1:
        details = ", ".join(
            f"{b['section_id']}/{b['block_id']}" for b in blocks
        )
        raise RuntimeError(
            f"Expected exactly 1 weekly image block, found {len(blocks)}: {details}"
        )

    block = blocks[0]
    current_week = block["week"]
    target_week = (
        args.target_week
        if args.target_week is not None
        else _next_week(current_week, args.wrap_at)
    )

    new_desktop_url = _url_with_week(block["image_url"], target_week)
    new_mobile_url = _url_with_week(block["mobile_image_url"], target_week)
    desktop_filename = _filename_from_url(new_desktop_url)
    mobile_filename = _filename_from_url(new_mobile_url)

    logger.info(
        "Weekly block: section=%s block=%s",
        block["section_id"],
        block["block_id"],
    )
    logger.info("Current desktop URL: %s", block["image_url"])
    logger.info("Current mobile URL: %s", block["mobile_image_url"])
    logger.info(
        "Week: %s -> %s (files: %s, %s)",
        current_week,
        target_week,
        desktop_filename,
        mobile_filename,
    )

    if args.skip_if_missing_images:
        missing = []
        if not _shop_image_exists(client, desktop_filename):
            missing.append(desktop_filename)
        if not _shop_image_exists(client, mobile_filename):
            missing.append(mobile_filename)
        if missing:
            logger.info(
                "Skip update: target image(s) not found in Shopify Files: %s",
                ", ".join(missing),
            )
            return

    new_content = _apply_weekly_update(current_content, block, target_week)
    logger.info("New desktop URL: %s", new_desktop_url)
    logger.info("New mobile URL: %s", new_mobile_url)

    if new_content == current_content:
        logger.info("No content changes.")
        return

    if args.dry_run:
        logger.info("Dry-run mode: no upsert executed.")
        return

    res = client.upsert_theme_file(theme["id"], args.theme_file, new_content)
    logger.info("Updated files: %s", res)


if __name__ == "__main__":
    main()
