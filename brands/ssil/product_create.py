import datetime
import logging
import zoneinfo
from brands.ssil.client import SsilClient

logging.basicConfig(level=logging.INFO)


def main():
    sheet_name = "NEW CLOVER"
    client = SsilClient(product_sheet_start_row=1)
    filter_func = lambda pi: pi["title"] not in ["CLOVER BAND R"]
    client.sanity_check_sheet(sheet_name, product_inputs_filter_func=filter_func)
    scheduled_time = datetime.datetime(
        2026, 3, 12, 12, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    client.process_sheet_to_products(
        sheet_name,
        scheduled_time=scheduled_time,
        additional_tags=["CLOVER", "New Arrival"],
        product_inputs_filter_func=filter_func
    )


if __name__ == "__main__":
    main()
