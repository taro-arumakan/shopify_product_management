"""Hero images and the home page's ALL STYLES tile list.

The ``list-collections`` section on ``templates/index.json`` renders one tile
per handle in its ``collection-list`` setting. With ``image-type: collection``
a tile uses the collection's own image and falls back to the first product
image when there is none -- so a collection without a hero shows a white
studio flatlay next to its neighbours' model shots.

Two jobs, both driven by the tables below:

* :data:`HERO_IMAGES` gives each new EPOKHE collection a model shot, taken from
  EPOKHE's own store. The tiles are square, so each was chosen on how it reads
  as a centre crop, matching the model-portrait convention of the tiles already
  there (GUILTY, WILSON, LOU).
* :data:`TILE_ORDER` is the list the section renders. Collections with nothing
  in stock are left out -- a tile that leads to an empty grid is worse than no
  tile.

    python -m brands.leisureallstars.collection_tiles          # report only
    python -m brands.leisureallstars.collection_tiles --apply  # write
"""

import json
import logging
import re
import sys

import utils

logger = logging.getLogger(__name__)

SHOP = "leisureallstars"
TEMPLATE = "templates/index.json"
SECTION_ID = "e14bed47-6cbc-4ca0-9349-10f9a1c5b0b4"

#: handle -> (image url on EPOKHE's store, alt text)
HERO_IMAGES = {
    "dome": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/11_2f595ded-6443-46b2-82b7-acea82de19bc.jpg",
        "EPOKHE DOME サングラス",
    ),
    "ember": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/ember-brown.jpg",
        "EPOKHE EMBER サングラス",
    ),
    "pano": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/PanoSunglasses-DarkTortoisePolishedBrown.jpg",
        "EPOKHE PANO サングラス",
    ),
    "ashfall-cap": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/EpokheAshfallCap-WashedRealTreeCamo.jpg",
        "EPOKHE ASHFALL CAP キャップ",
    ),
    "core-cap": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/EpokheCoreCap-WashedBlackCamo.jpg",
        "EPOKHE CORE CAP キャップ",
    ),
    "cave-trucker": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/Objects-Product-Images_6.jpg",
        "EPOKHE CAVE TRUCKER キャップ",
    ),
    "inferno-cap": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/EpokheInfernoCap-WashedBlackPinkRealTreeCamo.jpg",
        "EPOKHE INFERNO CAP キャップ",
    ),
    "stellar-cap": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/EpokheStellarCap-BlackContrastStitch.jpg",
        "EPOKHE STELLAR CAP キャップ",
    ),
    "tundra-trucker-cap": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/Objects-Product-Images_3.jpg",
        "EPOKHE TUNDRA TRUCKER CAP キャップ",
    ),
    # Collections that predate this batch and never had a hero: they were
    # falling back to a white studio flatlay beside their neighbours' portraits.
    # CANDY is discontinued at EPOKHE, so its shot comes from our own product
    # media; POLARIZED is a lens filter rather than a style and takes a shot of
    # a polarized colourway in bright sun.
    "coil": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/Coil-LightTortoisePolishedBronze.jpg",
        "EPOKHE COIL サングラス",
    ),
    "candy": (
        "https://cdn.shopify.com/s/files/1/0069/0782/2207/files/IMG-1550.jpg",
        "EPOKHE CANDY サングラス",
    ),
    "brut": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/Brut-army-green-mens-lifestyle_92985350-81e5-4a3a-900b-b7e3cd7edeef.jpg",
        "EPOKHE BRUT サングラス",
    ),
    "mono": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/mono.jpg",
        "EPOKHE MONO サングラス",
    ),
    "realm": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/RealmGunmetal.jpg",
        "EPOKHE REALM サングラス",
    ),
    "polarized": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/Reprise-black-bronze-womens-lifestyle.jpg",
        "EPOKHE 偏光レンズ サングラス",
    ),
    "thomas-townend-art-series-cap": (
        "https://cdn.shopify.com/s/files/1/0603/0909/files/EpokheThomasTownendArtSeriesHat-BlackOffWhite_1.jpg",
        "EPOKHE THOMAS TOWNEND ART SERIES CAP キャップ",
    ),
}

#: Eyewear keeps the order it had, with the new styles slotted into the
#: alphabetical run. Headwear is new to the store and groups after it.
#: "polarized" is a lens filter rather than a style and stays last, as before.
TILE_ORDER = [
    "superstar",
    "coil",
    "dylan",
    "brut",
    "candy",
    "ceremony",
    "desire",
    "dome",
    "dune",
    "ember",
    "frequency",
    "guilty",
    "memphis",
    "mono",
    "pano",
    "realm",
    "reprise",
    "stereo",
    "suede",
    "trinity",
    "veil",
    "wilson",
    "austyn",
    "ashfall-cap",
    "cave-trucker",
    "core-cap",
    "inferno-cap",
    "stellar-cap",
    "thomas-townend-art-series-cap",
    "tundra-trucker-cap",
    "polarized",
]

LIST_PATTERN = re.compile(
    r'(?P<head>"collection-list"\s*:\s*\[)(?P<body>.*?)(?P<tail>\])', re.DOTALL
)


def in_stock_counts(client):
    """``{handle: number of ACTIVE products with stock}`` for every collection."""
    query = """query($after:String){ collections(first:60, after:$after){
      pageInfo{hasNextPage endCursor}
      nodes{ handle image{url}
        products(first:250){ nodes{ status variants(first:30){nodes{inventoryQuantity}} } } } } }"""
    counts = {}
    for collection in client.run_paginated_query(
        query=query, variables={}, data_key="collections"
    ):
        counts[collection["handle"]] = {
            "instock": sum(
                1
                for product in collection["products"]["nodes"]
                if product["status"] == "ACTIVE"
                and any(
                    (v["inventoryQuantity"] or 0) > 0
                    for v in product["variants"]["nodes"]
                )
            ),
            "image": bool(collection["image"]),
        }
    return counts


def rewrite_collection_list(content, handles):
    """Replace only the collection-list array, leaving the rest byte for byte.

    The template carries a generated header comment, so it is not valid JSON and
    must not be round-tripped through json.dumps.
    """
    match = LIST_PATTERN.search(content)
    assert match, "collection-list array not found in the template"
    indent = re.search(r"\n(\s*)\"", match.group("body")).group(1)
    closing = re.search(r"\n(\s*)$", match.group("body"))
    body = "\n" + ",\n".join(f'{indent}"{h}"' for h in handles) + "\n"
    body += closing.group(1) if closing else ""
    return content[: match.start("body")] + body + content[match.end("body") :]


def main(testrun=True):
    logging.basicConfig(level=logging.INFO)
    client = utils.client(SHOP)
    theme = client.current_theme()
    counts = in_stock_counts(client)

    empty = [h for h in TILE_ORDER if counts.get(h, {}).get("instock", 0) == 0]
    assert not empty, f"these would render an empty grid: {empty}"
    unknown = [h for h in TILE_ORDER if h not in counts]
    assert not unknown, f"no such collection: {unknown}"

    content = client.theme_file_by_theme_name_and_file_name(theme["name"], TEMPLATE)[0][
        "body"
    ]["content"]
    before = json.loads(re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL))
    current = before["sections"][SECTION_ID]["settings"]["collection-list"]

    dropped = [h for h in current if h not in TILE_ORDER]
    added = [h for h in TILE_ORDER if h not in current]
    print(f"tiles: {len(current)} -> {len(TILE_ORDER)}")
    for handle in dropped:
        print(
            f"    drop {handle:<32} in stock: {counts.get(handle, {}).get('instock')}"
        )
    for handle in added:
        print(f"    add  {handle:<32} in stock: {counts[handle]['instock']}")

    for handle, (src, alt) in HERO_IMAGES.items():
        if testrun:
            logger.info(f"would set hero image on {handle}")
            continue
        collection = client.collections_by_query(f"handle:'{handle}'")
        assert len(collection) == 1, f"{len(collection)} collections for {handle!r}"
        client.update_collection_image(collection[0]["id"], src, alt)
        logger.info(f"hero image set on {handle}")

    updated = rewrite_collection_list(content, TILE_ORDER)
    after = json.loads(re.sub(r"/\*.*?\*/", "", updated, flags=re.DOTALL))
    changed = [
        key
        for key in set(before) | set(after)
        if json.dumps(before.get(key), sort_keys=True)
        != json.dumps(after.get(key), sort_keys=True)
    ]
    assert changed == ["sections"], f"unexpected top level change: {changed}"
    for key in set(before["sections"]) | set(after["sections"]):
        if key == SECTION_ID:
            continue
        assert before["sections"][key] == after["sections"][key], f"changed: {key}"
    settings_before = dict(before["sections"][SECTION_ID]["settings"])
    settings_after = dict(after["sections"][SECTION_ID]["settings"])
    settings_before.pop("collection-list")
    settings_after.pop("collection-list")
    assert settings_before == settings_after, "a setting other than the list moved"
    assert after["sections"][SECTION_ID]["settings"]["collection-list"] == TILE_ORDER

    if testrun:
        print("\ndry run -- template not written. Only collection-list would change.")
        return updated
    client.upsert_theme_file(theme["id"], TEMPLATE, updated)
    logger.info(f"{TEMPLATE} updated on {theme['name']}")
    return updated


if __name__ == "__main__":
    main(testrun="--apply" not in sys.argv)
