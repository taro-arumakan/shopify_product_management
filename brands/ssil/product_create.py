import datetime
import logging
import zoneinfo
from brands.ssil.client import SsilClient

logging.basicConfig(level=logging.INFO)


def main():
    sheet_name = "leather bag"
    client = SsilClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=True,
        products_season_tag="260708_leather_bag",
    )
    # filter_func = lambda pi: pi["title"] not in ["CLOVER BAND R"]
    client.sanity_check_sheet(sheet_name)
    scheduled_time = datetime.datetime(
        2026, 7, 8, 12, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    client.process_sheet_to_products(
        sheet_name,
        scheduled_time=scheduled_time,
        additional_tags=["New Arrival"],
    )


if __name__ == "__main__":
    main()
