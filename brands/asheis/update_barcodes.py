"""Backfill variant barcodes from the JANコード column (P) of products sheets.

For products already registered in Shopify before the JAN column existed.
Going forward, new products get their barcodes during creation
(AsheisClient.post_process_product_input).

Usage: update_barcodes.py [sheet_name ...]
"""

import logging
import sys
from brands.asheis.client import AsheisClient

logger = logging.getLogger(__name__)

DEFAULT_SHEETS = [
    "【8_9デリ】Products Master",
    "【0924デリ】Products Master",
]


def main():
    logging.basicConfig(level=logging.INFO)
    client = AsheisClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
    )
    errors = []
    for sheet_name in sys.argv[1:] or DEFAULT_SHEETS:
        product_inputs = client.product_inputs_by_sheet_name(sheet_name)
        logger.info(f"{sheet_name}: {len(product_inputs)} products")
        for pi in product_inputs:
            try:
                client.update_variant_barcodes(pi)
            except Exception as e:
                logger.error(f'{pi["title"]}: {e}')
                errors.append(f'{sheet_name} {pi["title"]}: {e}')
    if errors:
        raise SystemExit("\n".join(errors))


if __name__ == "__main__":
    main()
