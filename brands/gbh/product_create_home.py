import datetime
import logging
import zoneinfo
from brands.gbh.client import GbhHomeClient

logging.basicConfig(level=logging.INFO)


def fix_price():
    client = GbhHomeClient(use_simple_size_format=True)
    product_info_list = client.product_info_list_from_sheet(
        "bedding / ROBE (SIZE+COLOR)"
    )
    price_by_sku = {
        v2["sku"]: v2["price"]
        for p in product_info_list
        for v1 in p["options"]
        for v2 in v1["options"]
    }
    variants = [client.variant_by_sku(sku) for sku in price_by_sku.keys()]
    new_prices_by_variant_id = {
        v["id"]: p for v, p in zip(variants, price_by_sku.values())
    }
    client.update_variant_prices_by_dict(
        variants=variants,
        new_prices_by_variant_id=new_prices_by_variant_id,
        testrun=False,
    )


def main():

    client = GbhHomeClient(use_simple_size_format=True)
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    sheet_name = "bedding / ROBE (SIZE+COLOR)"

    # client = GbhClientColorOptionOnly()
    # client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    # sheet_name = "bedding / ROBE (COLOR ONLY)"

    client.sanity_check_sheet(sheet_name)

    scheduled_time = datetime.datetime(
        2026, 1, 16, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.process_sheet_to_products(
        sheet_name, additional_tags=["New Arrival"], scheduled_time=scheduled_time
    )


if __name__ == "__main__":
    fix_price()
