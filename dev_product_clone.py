import logging

logging.basicConfig(level=logging.INFO)

import datetime
import os
from brands.blossom.client import BlossomClientClothes


def main():

    client = BlossomClientClothes()
    client.shop_name = "quickstart-6f3c9e4c"
    client.access_token = os.environ["quickstart-6f3c9e4c-ACCESS_TOKEN"]
    client.base_url = (
        f"https://{client.shop_name}.myshopify.com/admin/api/2025-10/graphql.json"
    )
    client.LOCATIONS = ["Shop location", "My Custom Location"]

    sheet_names = ["clothes(drop11)", "clothes(drop12)", "clothes(jp exclusive)"]
    drop_tags = ["drop11", "drop12", "jp_exclusive"]

    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 1, 26, 18, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    for sheet_name in sheet_names:
        try:
            client.sanity_check_sheet(
                sheet_name, ignore_product_titles=["SOFFI CASHMERE V-NECK KNIT"]
            )
        except RuntimeError as e:
            logging.error(f"Sanity check failed for {sheet_name}: {e}")

    for sheet_name, drop_tag in zip(sheet_names, drop_tags):
        client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = sheet_name == "clothes(drop11)"

        client.process_sheet_to_products(
            sheet_name=sheet_name,
            additional_tags=[drop_tag, "New Arrival"],
            scheduled_time=scheduled_time,
            ignore_product_titles=["SOFFI CASHMERE V-NECK KNIT"],
        )


if __name__ == "__main__":
    main()
