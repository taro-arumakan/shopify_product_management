import logging

logging.basicConfig(level=logging.INFO)

import datetime
from brands.blossom.client import BlossomClientClothes


def update_series():
    sheet_name = "clothes(drop1) PS"

    client = BlossomClientClothes(product_sheet_start_row=1)
    product_inputs = client.product_inputs_by_sheet_name(sheet_name)
    products_by_series_names = {}
    for pi in product_inputs:
        products_by_series_names.setdefault(pi["series_name"], []).append(pi["title"])
    for series_name, titles in products_by_series_names.items():
        q = " OR ".join(f"title:'{title}'" for title in titles)
        products = client.products_by_query(q)
        logging.info(f"assigning {series_name} to {titles}")
        client.process_series_products(series_name, products)


def main():
    sheet_name = "clothes(drop1) PS"
    drop_tag = "2026_drop1"

    client = BlossomClientClothes(
        product_sheet_start_row=1, remove_existing_new_product_indicators=False
    )

    client.sanity_check_sheet(sheet_name, pre_rewrite=False)

    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 3, 10, 18, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.process_sheet_to_products(
        sheet_name=sheet_name,
        additional_tags=[drop_tag, "New Arrival"],
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    update_series()
