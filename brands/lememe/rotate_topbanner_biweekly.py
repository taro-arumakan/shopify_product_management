"""Rotate the LEMEME top-page hero banner to the next numbered image pair.

The TOP page's hero is a `slideshow` section, and the banner is the `image`
block in it whose images are a numbered tb_<season>_pc_NN / tb_<season>_m_NN
pair, e.g.
    "image":        "shopify://shop_images/tb_sepoct_pc_01.jpg"
    "mobile_image": "shopify://shop_images/tb_sepoct_m_01.jpg"
Each run advances the number by one (01 -> 02 -> ...) and wraps back to 01 when
the next pair is not in Content > Files, so the banners cycle.

Both the desktop and the mobile image move together — unlike ASHEIS, LEMEME
serves a separate 2:3 mobile crop, so the pair must stay in step.

The slideshow's other blocks carry one-off announcement images, so the banner
block is found by the tb_<season>_pc_NN filename rather than by its position in
the slides.

The season token (`sepoct`) is read from the live URL rather than hard-coded:
when the next season's images go up, point the block at tb_novdec_pc_01.jpg once
in the theme editor and this script keeps cycling within the new set unchanged.

The theme is fetched at run time (the live theme churns as banners/collections
are edited), and only the image URLs are substituted in the raw content — the
file is not re-serialised, so Shopify's auto-generated header comment and the
rest of the formatting survive. Same approach as brands/asheis.

NOT idempotent by design: every execute=True run advances one step, so a retried
or duplicated trigger skips a banner. Cosmetic here; if it ever matters, derive
the index from the date instead of incrementing.

Wire from Shopify Flow -> `run_func` GitHub Action (the every-two-weeks cadence
lives in the Flow trigger; this script just advances one step per run):
    script_path  brands/lememe/rotate_topbanner_biweekly.py
    func_name    rotate_topbanner
    params       {"execute": true}
"""

import logging
import re

import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BANNER_URL_PATTERN = re.compile(
    r"shopify://shop_images/tb_(?P<season>[a-z0-9]+)_pc_(?P<index>\d\d)\.jpg$"
)
DESKTOP_URL_TEMPLATE = "shopify://shop_images/tb_{season}_pc_{index:02d}.jpg"
MOBILE_URL_TEMPLATE = "shopify://shop_images/tb_{season}_m_{index:02d}.jpg"
FIRST_INDEX = 1  # LEMEME's banners are numbered from 01, not 00
SECTION_TYPE = "slideshow"
BLOCK_TYPE = "image"
DESKTOP_SETTING = "image"
MOBILE_SETTING = "mobile_image"
THEME_FILE = "templates/index.json"


def hero_banner(data):
    """Return (label, desktop_url, mobile_url) for the tb_ banner slide."""
    for section_key in data.get("order") or data["sections"]:
        section = data["sections"].get(section_key)
        if not section or section.get("type") != SECTION_TYPE:
            continue
        blocks = section.get("blocks") or {}
        for block_key in section.get("block_order") or blocks:
            block = blocks.get(block_key)
            if not block or block.get("type") != BLOCK_TYPE:
                continue
            settings = block.get("settings", {})
            desktop_url = settings.get(DESKTOP_SETTING) or ""
            if not BANNER_URL_PATTERN.match(desktop_url):
                continue
            mobile_url = settings.get(MOBILE_SETTING) or ""
            if not mobile_url:
                raise RuntimeError(
                    f"block {section_key}/{block_key} has {desktop_url} but no "
                    f"{MOBILE_SETTING} — the pair must rotate together"
                )
            return f"{section_key}/{block_key}", desktop_url, mobile_url
    raise RuntimeError(
        f"no {BLOCK_TYPE!r} block with a tb_<season>_pc_NN image found in a "
        f"{SECTION_TYPE!r} section of {THEME_FILE}"
    )


def file_exists(client, url):
    """file_by_file_name asserts when a file is missing, so treat that as False."""
    try:
        client.file_by_file_name(url.rsplit("/", 1)[-1])
        return True
    except AssertionError:
        return False


def banner_pair(season, index):
    return (
        DESKTOP_URL_TEMPLATE.format(season=season, index=index),
        MOBILE_URL_TEMPLATE.format(season=season, index=index),
    )


def pair_exists(client, desktop_url, mobile_url):
    """True when both crops are in Files; a half-uploaded pair is an error."""
    found = [file_exists(client, desktop_url), file_exists(client, mobile_url)]
    if all(found):
        return True
    if any(found):
        missing = desktop_url if not found[0] else mobile_url
        raise RuntimeError(
            f"incomplete banner pair — {missing} is missing from Files. "
            "Upload both the pc and the m crop, or neither."
        )
    return False


def next_banner_pair(client, current_desktop_url):
    """Return the next (desktop, mobile) pair, wrapping when the next is absent."""
    match = BANNER_URL_PATTERN.match(current_desktop_url)
    if not match:
        raise RuntimeError(f"unexpected banner url: {current_desktop_url!r}")
    season = match.group("season")

    candidate = banner_pair(season, int(match.group("index")) + 1)
    if pair_exists(client, *candidate):
        return candidate

    wrapped = banner_pair(season, FIRST_INDEX)
    logger.info("%s not found - wrapping to %s", candidate[0], wrapped[0])
    if not pair_exists(client, *wrapped):
        raise RuntimeError(f"neither {candidate[0]} nor {wrapped[0]} exists in Files")
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


def replace_once(content, current_url, new_url):
    if content.count(current_url) != 1:
        raise RuntimeError(
            f"expected exactly 1 occurrence of {current_url!r}, "
            f"found {content.count(current_url)}"
        )
    return content.replace(current_url, new_url, 1)


def rotate_topbanner(execute=False, theme_name=None):
    """run_func entrypoint — advance the hero banner in the live (MAIN) theme.

    kwargs-only; the run_func runner calls resolved_func(**params) with no client.
    Defaults to a dry run.
    """
    client = utils.client("lememe")
    theme = resolve_theme(client, theme_name)
    content = index_content(client, theme)

    block_label, current_desktop, current_mobile = hero_banner(
        client.theme_json_to_dict(content)
    )
    new_desktop, new_mobile = next_banner_pair(client, current_desktop)

    print(f"THEME {theme['name']} ({theme['id']}, role={theme['role']})")
    print(f"  block {block_label} ({SECTION_TYPE}/{BLOCK_TYPE})")
    print(f"  {current_desktop}  ->  {new_desktop}")
    print(f"  {current_mobile}  ->  {new_mobile}")

    if (new_desktop, new_mobile) == (current_desktop, current_mobile):
        print("\nOnly one banner available — nothing to rotate.")
        return

    new_content = replace_once(content, current_desktop, new_desktop)
    new_content = replace_once(new_content, current_mobile, new_mobile)

    if not execute:
        print("\nDRY RUN — no changes made. Set execute=True to apply.")
        return

    client.upsert_theme_file(theme["id"], THEME_FILE, new_content)
    print(f"  ✅ upserted {THEME_FILE}")

    # Re-read to confirm the change landed (this runs unattended).
    _, live_desktop, live_mobile = hero_banner(
        client.theme_json_to_dict(index_content(client, theme))
    )
    live = (live_desktop, live_mobile)
    expected = (new_desktop, new_mobile)
    print(f"  verify {'OK' if live == expected else f'MISMATCH {live!r}'}")


def main():
    rotate_topbanner(execute=False)


if __name__ == "__main__":
    main()
