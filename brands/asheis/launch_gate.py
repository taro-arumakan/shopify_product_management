"""Set and clear custom.launch_datetime for a scheduled drop.

The theme hides the add-to-cart button and shows the launch date while this
metafield is in the future, and the publication catch-up treats a product
with a future one as not yet launched, so it stays off the other sales
channels until the drop opens.

Clearing it at launch is optional - both gates compare against the clock, so
they open on their own - but the write invalidates the product's cached page,
which is what makes an already-rendered page pick up the change.

    PYTHONPATH=. uv run python -c "from brands.asheis.launch_gate import *; set_launch_datetime()"
    PYTHONPATH=. uv run python -c "from brands.asheis.launch_gate import *; set_launch_datetime(dry_run=False)"
"""

import logging

import utils
from helpers.shopify_graphql_client.publication_catch_up import (
    LAUNCH_DATETIME_KEY as KEY,
    LAUNCH_DATETIME_NAMESPACE as NAMESPACE,
)

logger = logging.getLogger(__name__)

TAG = "26_oct_1"
LAUNCH_AT = "2026-10-01T12:00:00+09:00"  # noon JST


def _products(client, tag):
    products = client.products_by_tag(tag)
    if not products:
        raise RuntimeError(f"no products tagged {tag!r}")
    return products


def set_launch_datetime(tag=TAG, launch_at=LAUNCH_AT, dry_run=True):
    client = utils.client("ASHEIS")
    products = _products(client, tag)
    logger.info(f"{len(products)} product(s) tagged {tag!r} -> {launch_at}")
    for product in products:
        logger.info(
            f"{'would set' if dry_run else 'setting'} {KEY} on {product['title']}"
        )
        if not dry_run:
            client.update_product_metafield(product["id"], NAMESPACE, KEY, launch_at)
    return len(products)


def clear_launch_datetime(tag=TAG, dry_run=True):
    client = utils.client("ASHEIS")
    products = _products(client, tag)
    for product in products:
        logger.info(
            f"{'would clear' if dry_run else 'clearing'} {KEY} on {product['title']}"
        )
        if not dry_run:
            # A falsy value deletes the metafield rather than writing a blank.
            client.update_product_metafield(product["id"], NAMESPACE, KEY, None)
    return len(products)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    set_launch_datetime()
