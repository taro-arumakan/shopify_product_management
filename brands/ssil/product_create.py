import datetime
import logging
import zoneinfo
from brands.ssil.client import SsilClient

logging.basicConfig(level=logging.INFO)


def main():
    sheet_name = "Essential Collection"
    client = SsilClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=True,
        products_season_tag="202609_essential_collection",
    )
    # filter_func = lambda pi: pi["title"] not in ["CLOVER BAND R"]
    # client.sanity_check_sheet(sheet_name)
    scheduled_time = datetime.datetime(
        2026, 9, 16, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    client.process_sheet_to_products(
        sheet_name,
        scheduled_time=scheduled_time,
        additional_tags=["essential_collection"],
        restart_at_product_title="X Pattern R",
    )


if __name__ == "__main__":
    main()
