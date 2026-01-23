import logging

logging.basicConfig(level=logging.INFO)

import datetime
from brands.blossom.client import BlossomClientClothes


def main():
    sheet_name = "clothes(drop11)_SOFFI CASHMERE V-NECK KNIT"
    drop_tag = "drop11"

    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 1, 26, 18, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client = BlossomClientClothes()

    client.sanity_check_sheet(sheet_name)

    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False

    client.process_sheet_to_products(
        sheet_name=sheet_name,
        additional_tags=[drop_tag, "New Arrival"],
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    main()
