"""Rotate the LEMEME top-page collection banners to the next numbered images.

Below the hero, the TOP page has a `collection-list` section whose `collection`
blocks (BAGS VIEW ALL / CLOTHES VIEW ALL) each show a numbered
<name>_view_all_N image, e.g.
    "image": "shopify://shop_images/bags_view_all_3.jpg"
    "image": "shopify://shop_images/clothes_view_all_3.jpg"
Each run advances every such banner by one (3 -> 4 -> ...) and wraps back to 1
when the next file is not in Content > Files, so the banners cycle.

The numbers are not zero-padded (bags_view_all_1 ... bags_view_all_8), unlike
the top banner's tb_<season>_pc_01.

Each banner cycles independently — bags wraps when bags_view_all_<N+1> is
missing, clothes when clothes_view_all_<N+1> is — so the two sets may hold
different numbers of images. The <name> is read from the live URL rather than
hard-coded, and the blocks are found by filename rather than by position.

The theme is fetched at run time (the live theme churns as banners/collections
are edited), and only the image URLs are substituted in the raw content — the
file is not re-serialised, so Shopify's auto-generated header comment and the
rest of the formatting survive. Same approach as rotate_topbanner_biweekly.py.

NOT idempotent by design: every execute=True run advances one step, so a retried
or duplicated trigger skips a banner. Cosmetic here; if it ever matters, derive
the index from the date instead of incrementing.

Wire from Shopify Flow -> `run_func` GitHub Action (the weekly cadence lives in
the Flow trigger; this script just advances one step per run):
    script_path  brands/lememe/rotate_collection_banners_weekly.py
    func_name    rotate_collection_banners
    params       {"execute": true}
"""

import logging
import re

import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BANNER_URL_PATTERN = re.compile(
    r"shopify://shop_images/(?P<name>[a-z0-9]+)_view_all_(?P<index>\d+)\.jpg$"
)
BANNER_URL_TEMPLATE = "shopify://shop_images/{name}_view_all_{index}.jpg"
FIRST_INDEX = 1  # numbered from 1, not 0
SECTION_TYPE = "collection-list"
BLOCK_TYPE = "collection"
IMAGE_SETTING = "image"
THEME_FILE = "templates/index.json"


def collection_banners(data):
    """Return [(label, image_url)] for every block holding a <name>_view_all_N image."""
    banners = []
    for section_key in data.get("order") or data["sections"]:
        section = data["sections"].get(section_key)
        if not section or section.get("type") != SECTION_TYPE:
            continue
        blocks = section.get("blocks") or {}
        for block_key in section.get("block_order") or blocks:
            block = blocks.get(block_key)
            if not block or block.get("type") != BLOCK_TYPE:
                continue
            image = block.get("settings", {}).get(IMAGE_SETTING) or ""
            if BANNER_URL_PATTERN.match(image):
                banners.append((f"{section_key}/{block_key}", image))
    if not banners:
        raise RuntimeError(
            f"no {BLOCK_TYPE!r} block with a <name>_view_all_N image found in a "
            f"{SECTION_TYPE!r} section of {THEME_FILE}"
        )
    return banners


def file_exists(client, url):
    """file_by_file_name asserts when a file is missing, so treat that as False.

    The lookup is a filename prefix search that skips its own exact-name filter
    when only one file comes back, so bags_view_all_1 would match a lone
    bags_view_all_10.jpg. Unpadded numbers make that reachable — check the name.
    """
    file_name = url.rsplit("/", 1)[-1]
    try:
        found = client.file_by_file_name(file_name)
    except AssertionError:
        return False
    found_url = (found.get("image") or {}).get("url") or ""
    return found_url.rsplit("?", 1)[0].endswith(f"/{file_name}")


def next_banner(client, current_url):
    """Return the next image url, wrapping to FIRST_INDEX when the next is absent."""
    match = BANNER_URL_PATTERN.match(current_url)
    if not match:
        raise RuntimeError(f"unexpected banner url: {current_url!r}")
    name = match.group("name")

    candidate = BANNER_URL_TEMPLATE.format(
        name=name, index=int(match.group("index")) + 1
    )
    if file_exists(client, candidate):
        return candidate

    wrapped = BANNER_URL_TEMPLATE.format(name=name, index=FIRST_INDEX)
    logger.info("%s not found - wrapping to %s", candidate, wrapped)
    if not file_exists(client, wrapped):
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


def replace_once(content, current_url, new_url):
    if content.count(current_url) != 1:
        raise RuntimeError(
            f"expected exactly 1 occurrence of {current_url!r}, "
            f"found {content.count(current_url)}"
        )
    return content.replace(current_url, new_url, 1)


def rotate_collection_banners(execute=False, theme_name=None):
    """run_func entrypoint — advance the collection banners in the live (MAIN) theme.

    kwargs-only; the run_func runner calls resolved_func(**params) with no client.
    Defaults to a dry run.
    """
    client = utils.client("lememe")
    theme = resolve_theme(client, theme_name)
    content = index_content(client, theme)

    banners = collection_banners(client.theme_json_to_dict(content))

    print(f"THEME {theme['name']} ({theme['id']}, role={theme['role']})")
    new_content = content
    expected = []
    for block_label, current_url in banners:
        new_url = next_banner(client, current_url)
        print(f"  block {block_label} ({SECTION_TYPE}/{BLOCK_TYPE})")
        print(f"    {current_url}  ->  {new_url}")
        if new_url != current_url:
            new_content = replace_once(new_content, current_url, new_url)
        expected.append(new_url)

    if new_content == content:
        print("\nOnly one image per banner available — nothing to rotate.")
        return

    if not execute:
        print("\nDRY RUN — no changes made. Set execute=True to apply.")
        return

    client.upsert_theme_file(theme["id"], THEME_FILE, new_content)
    print(f"  ✅ upserted {THEME_FILE}")

    # Re-read to confirm the change landed (this runs unattended).
    live = [
        url
        for _, url in collection_banners(
            client.theme_json_to_dict(index_content(client, theme))
        )
    ]
    print(f"  verify {'OK' if live == expected else f'MISMATCH {live!r}'}")


def main():
    rotate_collection_banners(execute=False)


if __name__ == "__main__":
    main()
