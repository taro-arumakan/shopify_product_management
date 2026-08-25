"""Register the new EPOKHE products from the SOH260818 order sheet.

Run the dry run first -- it makes no writes and prints the exact payload that
would be sent for each product::

    python -m brands.leisureallstars.product_create

Only once that output is signed off, call :func:`main` instead.
"""

import datetime
import logging
import os
import zoneinfo

from brands.leisureallstars import image_mapping
from brands.leisureallstars.client import EpokheClient

logger = logging.getLogger(__name__)

SHEET_NAME = "EPOKHEオーダーシート"
SEASON_TAG = "2608_EPOKHE"
#: Data rows are 12..124, and to_product_inputs slices rows[start_row:].
START_ROW = 11
FIRST_DATA_ROW = 12
LAST_DATA_ROW = 124

SCHEDULED_TIME = datetime.datetime(
    2026, 9, 1, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
)

#: Highlighted yellow by mistake -- already live as TRINITY BP/B with this SKU.
ALREADY_LIVE = {"0993-BLKPOBLK"}


def build_client():
    return EpokheClient(
        product_sheet_start_row=START_ROW,
        # The store is multi-vendor (ATLAS, AFENDS, ...) and the base's cleanup
        # is shop-wide, so it would strip "New Arrival" from other brands.
        remove_existing_new_product_indicators=False,
        products_season_tag=SEASON_TAG,
    )


def skus_to_create(client):
    """Yellow-highlighted SKUs, minus the ones we cannot or must not create."""
    highlighted = client.highlighted_skus(SHEET_NAME, FIRST_DATA_ROW, LAST_DATA_ROW)
    mapped = set(image_mapping.SKU_IMAGE_SOURCE)
    assert highlighted == mapped, (
        f"the sheet's highlighted rows no longer match image_mapping -- "
        f"only in sheet: {sorted(highlighted - mapped)}, "
        f"only in mapping: {sorted(mapped - highlighted)}"
    )
    no_images = {
        sku
        for sku, source in image_mapping.SKU_IMAGE_SOURCE.items()
        if source[2] == image_mapping.TODO
    }
    return highlighted - ALREADY_LIVE - no_images, no_images


def dry_run():
    """Print everything that would be sent. Makes no writes of any kind."""
    logging.basicConfig(level=logging.INFO)
    client = build_client()

    create_skus, no_images = skus_to_create(client)
    print(f"highlighted rows : {len(create_skus) + len(no_images) + len(ALREADY_LIVE)}")
    print(f"already live     : {sorted(ALREADY_LIVE)}")
    print(f"no images yet    : {sorted(no_images)}")
    print(f"to create        : {len(create_skus)}\n")
    assert create_skus, "nothing to create"

    product_inputs = client.product_inputs_by_sheet_name(SHEET_NAME)
    product_inputs = [pi for pi in product_inputs if pi["sku"] in create_skus]
    clashes = client.title_clashes(product_inputs)
    if clashes:
        print("*** title clashes -- resolve in EpokheClient.TITLE_OVERRIDES ***")
        for title, detail in sorted(clashes.items()):
            print(f"    {title:34} {detail['reason']}  {detail['skus']}")
        print()

    print(f"{'SKU':20} {'TITLE':34} {'HANDLE':34} {'PRICE':>7} {'STK':>4}  TYPE")
    print("-" * 118)
    for product_input in product_inputs:
        try:
            product_type = client.product_type_for(product_input)
        except AssertionError:
            product_type = "?? HEADWEAR_PRODUCT_TYPE unset"
        print(
            f"{product_input['sku']:20} {product_input['title'][:34]:34} "
            f"{product_input['handle'][:34]:34} {product_input['price']:>7} "
            f"{product_input['stock']:>4}  {product_type}"
        )

    print("\n=== payloads ===")
    missing_copy = []
    for product_input in product_inputs:
        options = client.populate_option_dicts(product_input)
        images = image_mapping.local_files(product_input["sku"])
        print(f"\n--- {product_input['title']}  [{product_input['sku']}]")
        print(f"  productOptions : {client.populate_product_options(options)}")
        print(f"  variants       : {client.populate_variant_inputs(options)}")
        print(f"  tags           : {client.get_tags(product_input, None)}")
        print(f"  sku -> stock   : {client.get_sku_stocks_map(product_input)}")
        print(f"  images ({len(images)})     : {[os.path.basename(p) for p in images]}")
        source, _html = client.description_source(product_input)
        if source is None:
            missing_copy.append(product_input["sku"])
            print("  description    : *** NONE -- no copy for this style ***")
        elif source == "live":
            print("  description    : reused from a live product of the same style")
        else:
            print("  description    : brands.leisureallstars.descriptions")

    if missing_copy:
        print(
            f"\n{len(missing_copy)} of {len(product_inputs)} products have no Japanese "
            f"copy and would fail on create:\n  {sorted(missing_copy)}"
        )
    print("\nNext: client.sanity_check_sheet(...) runs queries only, no writes.")
    return client, product_inputs


def main():
    logging.basicConfig(level=logging.INFO)
    client = build_client()
    create_skus, _ = skus_to_create(client)
    assert create_skus, "nothing to create"

    def product_inputs_filter_func(product_input):
        return product_input["sku"] in create_skus

    client.sanity_check_sheet(
        SHEET_NAME, product_inputs_filter_func=product_inputs_filter_func
    )
    client.process_sheet_to_products(
        SHEET_NAME,
        # "New Arrival" is prepended by BrandClientBase.get_tags already.
        additional_tags=None,
        scheduled_time=SCHEDULED_TIME,
        product_inputs_filter_func=product_inputs_filter_func,
    )


if __name__ == "__main__":
    dry_run()
