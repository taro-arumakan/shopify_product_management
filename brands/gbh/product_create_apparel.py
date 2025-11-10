import datetime
import logging
import zoneinfo
from brands.gbh.client import GbhClient

logging.basicConfig(level=logging.INFO)


def main():

    client = GbhClient()
    sheet_name = "APPAREL 25FW 2次"

    """
    From 25 Winter onward, only keep the products released in recent one year.
    e.g. archive 24FW before releasing 25FW.
    Refer to archive_products.py.
    """

    client.sanity_check_sheet(sheet_name)

    scheduled_time = datetime.datetime(
        2025, 11, 14, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival"],
        scheduled_time=scheduled_time)


if __name__ == "__main__":
    main()
