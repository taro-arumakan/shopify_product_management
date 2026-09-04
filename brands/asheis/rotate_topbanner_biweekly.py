"""Rotate the ASHEIS top-page hero banner to the next numbered image.

The TOP page's hero is a `slideshow` section, and the banner is the `image`
block in it whose image is a numbered tb_NN file, e.g.
    "image": "shopify://shop_images/tb_00.jpg"
Each run advances the number by one (tb_00 -> tb_01 -> ...) and wraps back to
tb_00 when the next file is not in Content > Files, so the banners cycle.

The slideshow's other blocks carry one-off announcement images, so the banner
block is found by the tb_NN filename rather than by its position in the slides.

Only the main image changes: mobile is forced to 393:762 by CSS, so there is no
separate mobile image to keep in step.

The theme is fetched at run time (the live theme churns as banners/collections
are edited), and only the image URL is substituted in the raw content — the file
is not re-serialised, so Shopify's auto-generated header comment and the rest of
the formatting survive. Same approach as update_theme_shipping_note.py.

NOT idempotent by design: every execute=True run advances one step, so a retried
or duplicated trigger skips a banner. Cosmetic here; if it ever matters, derive
the index from the date instead of incrementing.

Wire from Shopify Flow -> `run_func` GitHub Action (the every-two-weeks cadence
lives in the Flow trigger; this script just advances one step per run):
    script_path  brands/asheis/rotate_topbanner_biweekly.py
    func_name    rotate_topbanner
    params       {"execute": true}
"""

import logging
import re

import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BANNER_URL_PATTERN = re.compile(r"shopify://shop_images/tb_(\d\d)\.jpg$")
BANNER_URL_TEMPLATE = "shopify://shop_images/tb_{:02d}.jpg"
SECTION_TYPE = "slideshow"
BLOCK_TYPE = "image"
THEME_FILE = "templates/index.json"


def hero_banner(data):
    """Return (label, image_url) for the slideshow block holding the tb_NN banner."""
    for section_key in data.get("order") or data["sections"]:
        section = data["sections"].get(section_key)
        if not section or section.get("type") != SECTION_TYPE:
            continue
        blocks = section.get("blocks") or {}
        for block_key in section.get("block_order") or blocks:
            block = blocks.get(block_key)
            if not block or block.get("type") != BLOCK_TYPE:
                continue
            image = block.get("settings", {}).get("image") or ""
            if BANNER_URL_PATTERN.match(image):
                return f"{section_key}/{block_key}", image
    raise RuntimeError(
        f"no {BLOCK_TYPE!r} block with a tb_NN image found in a "
        f"{SECTION_TYPE!r} section of {THEME_FILE}"
    )


def file_exists(client, file_name):
    """file_by_file_name asserts when a file is missing, so treat that as False."""
    try:
        client.file_by_file_name(file_name)
        return True
    except AssertionError:
        return False


def next_banner_url(client, current_url):
    """Return the next banner URL, wrapping to tb_00 when the next is absent."""
    match = BANNER_URL_PATTERN.match(current_url)
    if not match:
        raise RuntimeError(f"unexpected banner url: {current_url!r}")

    candidate = BANNER_URL_TEMPLATE.format(int(match.group(1)) + 1)
    if file_exists(client, candidate.rsplit("/", 1)[-1]):
        return candidate

    wrapped = BANNER_URL_TEMPLATE.format(0)
    logger.info("%s not found - wrapping to %s", candidate, wrapped)
    if not file_exists(client, wrapped.rsplit("/", 1)[-1]):
        raise RuntimeError(f"neither {candidate} nor {wrapped} exists in Files")
    return wrapped


def resolve_theme(client, theme_name=None):
    if theme_name:
        themes = client.themes_by_names(theme_name)
        if len(themes) != 1:
            raise RuntimeError(f"theme not found or ambiguous: {theme_name!r}")
        return themes[0]
    theme = client.current_theme()
    if not theme:
        raise RuntimeError("no active theme found (role=MAIN)")
    return theme


def index_content(client, theme):
    nodes = [
        n
        for n in client.theme_file_by_theme_name_and_file_name(
            theme["name"], THEME_FILE
        )
        if n["filename"] == THEME_FILE
    ]
    if not nodes:
        raise RuntimeError(f"theme file not found: {THEME_FILE}")
    return nodes[0]["body"]["content"]


def rotate_topbanner(execute=False, theme_name=None):
    """run_func entrypoint — advance the hero banner in the live (MAIN) theme.

    kwargs-only; the run_func runner calls resolved_func(**params) with no client.
    Defaults to a dry run.
    """
    client = utils.client("asheis")
    theme = resolve_theme(client, theme_name)
    content = index_content(client, theme)

    block_label, current_url = hero_banner(client.theme_json_to_dict(content))
    new_url = next_banner_url(client, current_url)

    print(f"THEME {theme['name']} ({theme['id']}, role={theme['role']})")
    print(f"  block {block_label} ({SECTION_TYPE}/{BLOCK_TYPE})")
    print(f"  {current_url}  ->  {new_url}")

    if new_url == current_url:
        print("\nOnly one banner available — nothing to rotate.")
        return

    if content.count(current_url) != 1:
        raise RuntimeError(
            f"expected exactly 1 occurrence of {current_url!r}, "
            f"found {content.count(current_url)}"
        )
    new_content = content.replace(current_url, new_url, 1)

    if not execute:
        print("\nDRY RUN — no changes made. Set execute=True to apply.")
        return

    client.upsert_theme_file(theme["id"], THEME_FILE, new_content)
    print(f"  ✅ upserted {THEME_FILE}")

    # Re-read to confirm the change landed (this runs unattended).
    _, live_url = hero_banner(client.theme_json_to_dict(index_content(client, theme)))
    print(f"  verify {'OK' if live_url == new_url else f'MISMATCH {live_url!r}'}")


def main():
    rotate_topbanner(execute=False)


if __name__ == "__main__":
    main()
