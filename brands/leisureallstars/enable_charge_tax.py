"""Turn Shopify's "Charge tax" on for every leisureallstars variant missing it.

    python -m brands.leisureallstars.enable_charge_tax                # report only
    python -m brands.leisureallstars.enable_charge_tax --apply --limit 1
    python -m brands.leisureallstars.enable_charge_tax --apply        # the rest

The store prices tax-inclusive, so this does not move a single price: a 27,500
yen variant still charges 27,500 yen afterwards. It changes how the order is
booked -- 27,500 net and no 消費税 becomes 25,000 + 2,500. See
:mod:`.list_untaxed_variants` for why that matters and for the read-only list.

Because the price must not move, every mutation asks for ``price`` back and
this script asserts it is unchanged. A variant whose price shifts aborts the
run rather than letting a pricing bug spread across the catalogue.

Safe to re-run: it reads the current state each time and touches only what is
still false, so a run cut short halfway leaves nothing to clean up -- run it
again and it picks up where it stopped. It skips the rows
:mod:`.list_untaxed_variants` flags as needing a decision (gift cards, which
are 不課税 until redemption, and anything not requiring shipping).

This fixes new orders only. Orders already placed keep the zero tax they were
booked with; Shopify will not recalculate them.
"""

import argparse
import logging
import sys
import time

import utils
from brands.leisureallstars.list_untaxed_variants import (
    SHOP,
    all_variants,
    fit,
    needs_a_decision,
    to_row,
    yen,
)

logger = logging.getLogger(__name__)

#: productVariantsBulkUpdate is scoped to one product, so the work is one call
#: per product however few variants it has.
RETRIES = 3
RETRY_WAIT = 2


def by_product(variants):
    """``{product gid: [variant, ...]}`` preserving the store's order."""
    grouped = {}
    for variant in variants:
        grouped.setdefault(variant["product"]["id"], []).append(variant)
    return grouped


def targets(client):
    """Variants to flip, and the ones deliberately left alone."""
    variants = [v for v in all_variants(client) if not v["taxable"]]
    flip, skip = [], []
    for variant in variants:
        (skip if needs_a_decision(to_row(variant)) else flip).append(variant)
    return flip, skip


def enable(client, product_id, variants):
    """Set taxable on one product's variants; assert no price moved."""
    before = {v["id"]: v["price"] for v in variants}
    variables = {
        "productId": product_id,
        "variants": [{"id": v["id"], "taxable": True} for v in variants],
    }
    for attempt in range(1, RETRIES + 1):
        try:
            res = client.run_variants_bulk_update(
                variables=variables, return_fields=["taxable", "price"]
            )
            break
        except RuntimeError as exception:
            # The bucket refills on its own; anything else is a real failure.
            if "THROTTLED" not in str(exception).upper() or attempt == RETRIES:
                raise
            logger.warning(f"throttled on {product_id}, retry {attempt}")
            time.sleep(RETRY_WAIT * attempt)

    for updated in res["productVariants"]:
        was = before[updated["id"]]
        assert float(updated["price"]) == float(was), (
            f"{updated['id']} moved from {was} to {updated['price']} -- the store is "
            f"not pricing tax-inclusive after all. Nothing further will be changed; "
            f"revert this product by hand before re-running."
        )
        assert updated["taxable"], f"{updated['id']} is still not taxable"
    return res["productVariants"]


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--apply", action="store_true", help="write to the store (default: report only)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="stop after this many products -- use --limit 1 for a first pass",
    )
    args = parser.parse_args()

    client = utils.client(SHOP)
    flip, skip = targets(client)
    grouped = by_product(flip)

    for row in (to_row(v) for v in skip):
        print(f"  leaving alone: {row['sku'] or row['product_title']}")

    product_ids = list(grouped)
    if args.limit:
        product_ids = product_ids[: args.limit]

    total = sum(len(grouped[pid]) for pid in product_ids)
    if not total:
        print("nothing to do -- every variant already has Charge tax on.")
        return 0
    if not args.apply:
        print(
            f"\nwould set taxable on {total} variants across {len(product_ids)} "
            f"products. Re-run with --apply to write."
        )
        return 0

    done = 0
    for index, product_id in enumerate(product_ids, start=1):
        variants = grouped[product_id]
        title = variants[0]["product"]["title"]
        print(
            f"  [{index}/{len(product_ids)}] {fit(title, 46)}  "
            f"{len(variants)} variant(s)  {yen(variants[0]['price'])}"
        )
        enable(client, product_id, variants)
        done += len(variants)

    print(f"\nset taxable on {done} variants across {len(product_ids)} products.")
    if args.limit:
        print("run again without --limit for the rest.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
