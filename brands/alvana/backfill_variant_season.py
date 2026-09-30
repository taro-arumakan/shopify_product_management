"""OT-28: set custom.product_variant_season on the variants of one season's products.

The 26SS run set this per variant through its own script, so the registration flow never
did it and the 26AW products came out without it. update_metafields now sets it at
registration, which leaves the products already registered to be backfilled -- this does
that, and stays useful for any season whose products predate the change.

Products are selected by season tag, and only variants missing the metafield are written,
so it is safe to repeat. Variants added to a product of an EARLIER season (a new colourway
on a carry-over product, a colourway promoted out of a twin) are deliberately out of
scope: the product's tag is the wrong answer for them and only the brand can say which
season they belong to.

Run with DRY_RUN = True first: it lists what it would set and writes nothing.
"""

import logging

from brands.alvana.client import AlvanaClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DRY_RUN = True
SEASON = "26aw"  # the tag to select on, and the value written

PRODUCTS_QUERY = """query($after:String){ products(first:50, after:$after){
  pageInfo{hasNextPage endCursor}
  nodes{ id title status tags
    variants(first:60){nodes{ id sku
      metafield(namespace:"custom", key:"product_variant_season"){ value } }} } } }"""


def main():
    client = AlvanaClient(product_sheet_start_row=1)
    products, after = [], None
    while True:
        page = client.run_query(PRODUCTS_QUERY, {"after": after})["products"]
        products += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        after = page["pageInfo"]["endCursor"]

    todo = []
    for product in products:
        if product["status"] == "ARCHIVED" or SEASON not in product["tags"]:
            continue
        missing = [
            v
            for v in product["variants"]["nodes"]
            if not (v.get("metafield") or {}).get("value")
        ]
        if missing:
            todo.append((product, missing))

    total = sum(len(v) for _, v in todo)
    logger.info(
        f"{len(todo)} product(s) tagged {SEASON!r}, {total} variant(s) without the metafield"
    )
    for product, missing in todo:
        logger.info(
            f"  {product['title'][:52]:52} {len(missing)}/{len(product['variants']['nodes'])}"
        )
    if DRY_RUN:
        logger.info("DRY_RUN: nothing written")
        return

    for product, missing in todo:
        logger.info(
            f"setting {SEASON!r} on {len(missing)} variant(s) of {product['title']!r}"
        )
        for variant in missing:
            client.update_variant_metafield(
                product["id"], variant["id"], "custom", "product_variant_season", SEASON
            )
    logger.info(f"done: {total} variant(s) set to {SEASON!r}")


if __name__ == "__main__":
    main()
