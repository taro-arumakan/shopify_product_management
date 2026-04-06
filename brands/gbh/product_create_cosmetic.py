import datetime
import logging
import zoneinfo
from brands.gbh.client import GbhClientColorOptionOnly, GbhCosmeticClient

logging.basicConfig(level=logging.INFO)

FILTER_COSMETIC_TITLES = ["POCKET MULTI BALM", "TRAVEL KIT (single)"]
TAG = "26SS_2nd"


def main():
    client = GbhCosmeticClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag=TAG,
    )

    sheet_name = "26.04.07マルチバームオープン(26.04.07멀티밤오픈)"
    filter_func = lambda pi: pi["title"] in FILTER_COSMETIC_TITLES
    client.sanity_check_sheet(sheet_name, product_inputs_filter_func=filter_func)

    scheduled_time = datetime.datetime(
        2026, 3, 10, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    # client.process_sheet_to_products(
    #     sheet_name,
    #     additional_tags=["New Arrival", "26SS_2nd_cosme"],
    #     product_inputs_filter_func=filter_func,
    #     scheduled_time=scheduled_time,
    # )


if __name__ == "__main__":
    main()
