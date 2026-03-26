import datetime
import logging
import zoneinfo
from brands.ssil.client import SsilClient

logging.basicConfig(level=logging.INFO)


def main():
    sheet_name = "NEW X ROW"
    client = SsilClient(
        product_sheet_start_row=1, remove_existing_new_product_indicators=True
    )
    # filter_func = lambda pi: pi["title"] not in ["CLOVER BAND R"]
    client.sanity_check_sheet(sheet_name)
    scheduled_time = datetime.datetime(
        2026, 3, 27, 12, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    client.process_sheet_to_products(
        sheet_name,
        scheduled_time=scheduled_time,
        additional_tags=["X", "New Arrival", "26_0327X-ROW"],
    )


if __name__ == "__main__":
    main()
