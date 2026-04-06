import datetime
import logging
import zoneinfo
from brands.gbh.client import GbhHomeClient

logging.basicConfig(level=logging.INFO)


def main():

    client = GbhHomeClient(
        product_sheet_start_row=1,
        use_simple_size_format=False,
        remove_existing_new_product_indicators=False,
        products_season_tag="26SS_2nd",
    )
    sheet_name = "26.04.07パジャマオープン(26.04.07파자마오픈)"

    client.sanity_check_sheet(sheet_name)

    scheduled_time = datetime.datetime(
        2026, 2, 27, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    # client.process_sheet_to_products(
    #     sheet_name,
    #     additional_tags=["New Arrival", "26SS_2nd_pajamas"],
    #     scheduled_time=scheduled_time
    # )


if __name__ == "__main__":
    main()
