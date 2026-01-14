import datetime
import logging
import zoneinfo
from brands.gbh.client import GbhClientColorOptionOnly
from brands.gbh.client import GbhClient

logging.basicConfig(level=logging.INFO)


def main():

    client = GbhClient(use_simple_size_format=True)
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
    main()
