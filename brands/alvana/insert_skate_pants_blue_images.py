"""OT-28: add the 26AW BLUE shots to BHARAT DENIM SKATE PANTS, in front of BLACK.

The consolidated product reads BLUE (12 images) / BLACK (5) / INK BLACK (5). An upload
always lands at the end of the gallery, so appending the 5 new BLUE shots would leave the
order BLUE, BLACK, INK BLACK, BLUE. They are uploaded and then moved to the end of the
existing BLUE block, which is where the BLACK block starts.

Colour blocks are found by each variant's featured image rather than with
medias_by_variant_id, which assumes evenly sized blocks (12/5/5 here fails its assert).

Run with DRY_RUN = True first: it prints the resulting order and writes nothing.
"""

import datetime
import logging
import pathlib

from brands.alvana.product_create_26aw import (
    Alvana26AWClient,
    SEASON_TAG,
    is_already_on_product,
    load_product_inputs,
    media_name,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DRY_RUN = True
PRODUCT_TITLE = "BHARAT DENIM SKATE PANTS"
COLOUR = "BLUE"
NEXT_COLOUR = "BLACK"  # the new images go immediately before this colour's first image
LOCAL_DIR = (
    pathlib.Path.home()
    / "Downloads"
    / f"alvana_skate_blue_{datetime.date.today():%Y%m%d}"
)

PRODUCT_QUERY = """query($id:ID!){ product(id:$id){
  id title
  media(first:250){nodes{ id ... on MediaImage{ image{ url } } }}
  variants(first:100){nodes{ id sku title
    media(first:1){nodes{ id }} }} } }"""


def product_state(client, product_id):
    product = client.run_query(PRODUCT_QUERY, {"id": product_id})["product"]
    media_ids = [m["id"] for m in product["media"]["nodes"]]
    return product, media_ids


def first_media_position(product, media_ids, colour):
    """Where this colour's block starts, from the featured image of its first variant."""
    for variant in product["variants"]["nodes"]:
        if variant["title"].split(" / ")[0] != colour:
            continue
        featured = variant["media"]["nodes"]
        if featured:
            return media_ids.index(featured[0]["id"])
    raise RuntimeError(f"no variant of {colour!r} carries a featured image")


def main():
    client = Alvana26AWClient(
        product_sheet_start_row=1,
        products_season_tag=SEASON_TAG,
        remove_existing_new_product_indicators=False,
    )
    product_id = client.product_id_by_title(PRODUCT_TITLE)
    product, media_ids = product_state(client, product_id)

    colour_option = next(
        o
        for pi in load_product_inputs(client)
        if pi["title"] == PRODUCT_TITLE
        for o in pi["options"]
        if o["カラー"] == COLOUR
    )
    on_product = {
        media_name(m["image"]["url"])
        for m in product["media"]["nodes"]
        if m.get("image")
    }
    files = sorted(
        client.get_drive_image_details(
            client.drive_link_to_id(colour_option["drive_link"])
        ),
        key=lambda f: f["name"],
    )
    to_add = [f for f in files if not is_already_on_product(f["name"], on_product)]

    insert_at = first_media_position(product, media_ids, NEXT_COLOUR)
    logger.info(
        f"{product['title']!r}: {len(media_ids)} images, "
        f"{NEXT_COLOUR} starts at position {insert_at}"
    )
    logger.info(
        f"  adding {len(to_add)} {COLOUR} image(s) at {insert_at}: "
        f"{[f['name'] for f in to_add]}"
    )
    if not to_add:
        logger.info("nothing to add")
        return
    if DRY_RUN:
        logger.info("DRY_RUN: nothing written")
        return

    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    local_paths = [
        client.download_and_process_image(
            f["id"],
            str(
                LOCAL_DIR
                / f"insert_{colour_option['options'][0]['sku']}_{seq:03}_{f['name']}"
            ),
        )
        for seq, f in enumerate(to_add)
    ]
    res = client.upload_and_assign_images_to_product(product_id, local_paths, False)
    added = [m["id"] for m in res[-1]["productCreateMedia"]["media"]]
    logger.info(
        f"  uploaded {len(added)} media, now moving them to position {insert_at}"
    )

    # rebuild the whole gallery: everything before the insert point, the new images, then
    # the rest, with the appended copies taken out of the tail
    _, media_ids = product_state(client, product_id)
    tail = [m for m in media_ids if m not in added]
    ordered = tail[:insert_at] + added + tail[insert_at:]
    client.reorder_product_medias(product_id, ordered)
    logger.info(
        f"  gallery is now {len(ordered)} images with {COLOUR} additions at {insert_at}"
    )


if __name__ == "__main__":
    main()
