"""OT-28: fold the three BHARAT DENIM SKATE PANTS products into one.

The shop carries the same item three times: the 2024 BLUE product, a 2025 BLACK one
whose option is named 色/ブラック rather than カラー/BLACK, and the 26SS '(no image)'
twin holding INK BLACK. The 26AW sheet lists one product with BLUE and INK BLACK, and
BK / IBK are confirmed to be different colourways.

'bharat-skate-denim-pants' survives, because it is the oldest handle, carries the most
media and sits in the most collections. It is renamed to BHARAT DENIM SKATE PANTS and
gains BLACK (variants, stock and images carried over from the retired product) and INK
BLACK (new, from the sheet's drive folder).

The two retired products are ARCHIVED, never deleted: archiving takes them off the
storefront just as well, keeps their order and analytics history readable, and can be
undone if any of this turns out wrong. Their handles redirect to the survivor.

Order matters: the snapshot is taken before anything is touched, and the retired
products are archived before the survivor gains their SKUs, so no SKU is live twice.
"""

import datetime
import logging
import pathlib
import urllib.request

from brands.alvana.client import AlvanaClient
from brands.alvana.product_create_26aw import (
    FILTER_COLOUR_ALIASES,
    SEASON_TAG,
    SHEET_NAME,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DRY_RUN = True

SURVIVOR_HANDLE = "bharat-skate-denim-pants"
SURVIVOR_TITLE = "BHARAT DENIM SKATE PANTS"
RETIRED_TITLES = [
    "BHARAT DENIM SKATE PANTS BLACK",
    "BHARAT DENIM SKATE PANTS (no image)",
]
# The retired BLACK product says 色/ブラック; everything else on the shop says カラー/BLACK.
BLACK_OPTION_VALUE = "BLACK"
LOCAL_DIR = (
    pathlib.Path.home()
    / "Downloads"
    / f"alvana_skate_pants_{datetime.date.today():%Y%m%d}"
)

PRODUCTS_QUERY = """query($after:String){ products(first:100, after:$after){
  pageInfo{hasNextPage endCursor}
  nodes{ id title handle status tags
    options{ name values }
    media(first:60){nodes{... on MediaImage{ image{ url altText } }}}
    variants(first:60){nodes{ id sku title price inventoryQuantity
      metafield(namespace:"custom", key:"filter_color"){ value } }} } } }"""


def all_products(client):
    products, after = [], None
    while True:
        page = client.run_query(PRODUCTS_QUERY, {"after": after})["products"]
        products += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        after = page["pageInfo"]["endCursor"]
    return products


def snapshot(client):
    """The three products as they stand, before anything is touched."""
    products = {p["title"]: p for p in all_products(client)}
    survivor = next(p for p in products.values() if p["handle"] == SURVIVOR_HANDLE)
    retired = [products[title] for title in RETIRED_TITLES]
    for product in [survivor] + retired:
        logger.info(f"{product['title']!r} ({product['status']}, {product['handle']})")
        for variant in product["variants"]["nodes"]:
            logger.info(
                f"    {variant['sku']:20} {variant['title']:16} "
                f"¥{variant['price']} stock={variant['inventoryQuantity']}"
            )
    return survivor, retired


def download_media(product, prefix):
    """Shopify media cannot move between products, so the images come down and go back
    up under the survivor."""
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for seq, media in enumerate(product["media"]["nodes"]):
        if not media.get("image"):
            continue
        url = media["image"]["url"]
        name = url.split("/")[-1].split("?")[0]
        path = LOCAL_DIR / f"{prefix}_{seq:03}_{name}"
        if not path.exists():
            urllib.request.urlretrieve(url, path)
        paths.append(str(path))
    return paths


def add_colourway(client, product_id, colour, variants, local_paths, filter_colour):
    """Add one colourway to the survivor: images first, then the variants pointing at
    the first of them, then the storefront filter metafield."""
    location_id = client.location_id_by_name(client.LOCATIONS[0])
    media_ids = []
    if local_paths:
        res = client.upload_and_assign_images_to_product(
            product_id, local_paths, False  # keep the survivor's own media
        )
        media_ids = [m["id"] for m in res[-1]["productCreateMedia"]["media"]]
    client.variants_add(
        product_id=product_id,
        skus=[v["sku"] for v in variants],
        media_ids=[],
        variant_media_ids=[media_ids[0] if media_ids else None] * len(variants),
        option_names=["カラー", "サイズ"],
        variant_option_valuess=[[colour, v["size"]] for v in variants],
        prices=[v["price"] for v in variants],
        stocks=[v["stock"] for v in variants],
        location_id=location_id,
    )
    for variant in variants:
        variant_id = client.variant_id_by_sku(variant["sku"])
        client.update_variant_metafield(
            product_id, variant_id, "custom", "filter_color", filter_colour
        )


def black_variants(retired_black):
    """BK-2/3/4 as they stand on the retired product, stock included."""
    return [
        {
            "sku": variant["sku"],
            "size": variant["title"].split(" / ")[-1],
            "price": variant["price"],
            "stock": variant["inventoryQuantity"],
        }
        for variant in retired_black["variants"]["nodes"]
    ]


def ink_black_variants(client):
    """IBK-1..4 from the sheet, at 0 stock like every other 26AW registration."""
    product_input = next(
        pi
        for pi in client.product_inputs_by_sheet_name(SHEET_NAME)
        if pi["title"] == SURVIVOR_TITLE
    )
    colour_option = next(
        o for o in product_input["options"] if o["カラー"] == "INK BLACK"
    )
    variants = [
        {
            "sku": size_option["sku"],
            "size": size_option["サイズ"],
            "price": product_input["price"],
            "stock": 0,
        }
        for size_option in colour_option["options"]
    ]
    return (
        variants,
        colour_option["drive_link"],
        FILTER_COLOUR_ALIASES.get(
            colour_option["filter_color"], colour_option["filter_color"]
        ),
    )


def main():
    client = AlvanaClient(
        product_sheet_start_row=1,
        products_season_tag=SEASON_TAG,
        remove_existing_new_product_indicators=False,
    )
    survivor, retired = snapshot(client)
    retired_black, retired_twin = retired
    black = black_variants(retired_black)
    ink_black, ink_black_link, ink_black_filter = ink_black_variants(client)

    logger.info(f"\nsurvivor: {survivor['title']!r} -> {SURVIVOR_TITLE!r}")
    logger.info(
        f"  + BLACK      {[(v['sku'], v['stock']) for v in black]} "
        f"with {len(retired_black['media']['nodes'])} image(s) carried over"
    )
    logger.info(
        f"  + INK BLACK  {[(v['sku'], v['stock']) for v in ink_black]} "
        f"from {ink_black_link}"
    )
    logger.info(f"  archiving: {[p['title'] for p in retired]}")
    if DRY_RUN:
        logger.info("DRY_RUN: nothing written")
        return

    black_paths = download_media(retired_black, "black")
    ink_black_paths = client.drive_images_to_local(
        client.drive_link_to_id(ink_black_link), str(LOCAL_DIR), "ink_black"
    )

    # archive first: the survivor must not hold a duplicate live SKU while it is built
    for product in retired:
        logger.info(f"archiving {product['title']!r}")
        client.update_product_status(product["id"], "ARCHIVED")

    add_colourway(
        client, survivor["id"], BLACK_OPTION_VALUE, black, black_paths, "BLACK"
    )
    add_colourway(
        client,
        survivor["id"],
        "INK BLACK",
        ink_black,
        ink_black_paths,
        ink_black_filter,
    )
    client.update_product_title(survivor["id"], SURVIVOR_TITLE)

    for product in retired:
        logger.info(f"redirecting {product['handle']!r} to the survivor")
        client.create_url_redirect(
            f"/products/{product['handle']}", f"/products/{SURVIVOR_HANDLE}"
        )


if __name__ == "__main__":
    main()
