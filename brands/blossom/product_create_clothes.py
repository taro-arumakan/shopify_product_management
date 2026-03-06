import logging

logging.basicConfig(level=logging.INFO)

import datetime
from brands.blossom.client import BlossomClientClothes


def main():
    sheet_name = "clothes(drop1) PS"
    drop_tag = "2026_drop1"

    client = BlossomClientClothes(product_sheet_start_row=1)

    client.sanity_check_sheet(sheet_name, pre_rewrite=False)

    # # client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False

    # import zoneinfo

    # scheduled_time = datetime.datetime(
    #     2026, 3, 10, 18, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    # )

    # client.process_sheet_to_products(
    #     sheet_name=sheet_name,
    #     additional_tags=[drop_tag, "New Arrival"],
    #     scheduled_time=scheduled_time,
    # )


if __name__ == "__main__":
    main()
