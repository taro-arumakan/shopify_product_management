import datetime
import logging
import zoneinfo
from brands.gbh.client import GbhClientNoOptions

logging.basicConfig(level=logging.INFO)


def main():

    client = GbhClientNoOptions()
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    sheet_name = "福袋(복주머니)"

    client.sanity_check_sheet(sheet_name)

    scheduled_time = datetime.datetime(
        2026, 1, 1, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.process_sheet_to_products(
        sheet_name, additional_tags=["New Arrival"], scheduled_time=scheduled_time
    )


if __name__ == "__main__":
    main()
