"""OT-28: finish a 26AW product that was created but not completed.

Registration creates the product, uploads its images, sets its metafields and publishes,
in that order. A transient failure in the middle leaves a DRAFT with variants and no
images -- and the main script will not notice, because its planner sees the SKUs on the
shop and reads the colourway as already registered.

This finds products whose SKUs come from the sheet but which are still DRAFT, and runs
the steps that did not get to run. Safe to repeat: images already on the product are
skipped by name, and the rest is idempotent.

Run with DRY_RUN = True first: it lists what it would finish and writes nothing.
"""

import logging

from brands.alvana.product_create_26aw import (
    Alvana26AWClient,
    SEASON_TAG,
    load_product_inputs,
    shop_index,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DRY_RUN = False

PRODUCTS_QUERY = """query($after:String){ products(first:100, after:$after){
  pageInfo{hasNextPage endCursor}
  nodes{ id title status
    media(first:100){nodes{ id }}
    variants(first:100){nodes{ sku }} } } }"""


def draft_products(client):
    products, after = [], None
    while True:
        page = client.run_query(PRODUCTS_QUERY, {"after": after})["products"]
        products += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        after = page["pageInfo"]["endCursor"]
    return [p for p in products if p["status"] == "DRAFT"]


def main():
    client = Alvana26AWClient(
        product_sheet_start_row=1,
        products_season_tag=SEASON_TAG,
        remove_existing_new_product_indicators=False,
    )
    product_inputs = load_product_inputs(client)
    by_sku = shop_index(client)
    sheet_skus = {
        size_option["sku"]: product_input
        for product_input in product_inputs
        for colour_option in product_input["options"]
        for size_option in colour_option["options"]
        if size_option.get("sku")
    }

    unfinished = []
    for product in draft_products(client):
        skus = [v["sku"] for v in product["variants"]["nodes"] if v["sku"]]
        owner = next((sheet_skus[s] for s in skus if s in sheet_skus), None)
        if owner:
            unfinished.append((product, owner))

    if not unfinished:
        logger.info("no draft product of this sheet to finish")
        return
    for product, product_input in unfinished:
        logger.info(
            f"{product['title']!r} is DRAFT with {len(product['media']['nodes'])} image(s) "
            f"-- would upload images, set metafields and publish"
        )
    if DRY_RUN:
        logger.info("DRY_RUN: nothing written")
        return

    for product, product_input in unfinished:
        logger.info(f"finishing {product['title']!r}")
        # the sheet product may be split across a live product and its twin; only the
        # colourways whose SKUs are on THIS product belong here
        on_product = {v["sku"] for v in product["variants"]["nodes"] if v["sku"]}
        subset = dict(
            product_input,
            title=product["title"],
            options=[
                colour_option
                for colour_option in product_input["options"]
                if any(s["sku"] in on_product for s in colour_option["options"])
            ],
        )
        client.process_product_images(subset)
        client.update_metafields(product["id"], subset)
        client.update_weight(list(on_product), subset)
        client.activate_and_publish_by_product_id(product["id"])
        logger.info(f"  {product['title']!r} published")


if __name__ == "__main__":
    main()
