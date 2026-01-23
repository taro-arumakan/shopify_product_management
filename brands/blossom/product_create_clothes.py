import logging

logging.basicConfig(level=logging.INFO)

import datetime
from brands.blossom.client import BlossomClientClothes


def main():
    sheet_names = ["clothes(drop11)", "clothes(drop12)", "clothes(jp exclusive)"]
    drop_tags = ["drop11", "drop12", "jp_exclusive"]

    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 1, 26, 18, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client = BlossomClientClothes()

    for sheet_name in sheet_names:
        try:
            client.sanity_check_sheet(sheet_name)
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
