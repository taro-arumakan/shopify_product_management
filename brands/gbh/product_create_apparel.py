import datetime
import logging
import zoneinfo
from brands.gbh.client import GbhClient, GbhClientColorOptionOnly

logging.basicConfig(level=logging.INFO)

EXCLUDE_APPAREL_TITLES = ["GARDEN BAG SMALL", "TULIP BAG"]
TAG = "26SS_3.10"

def create_26ss_color_only():
    client = GbhClientColorOptionOnly(product_sheet_start_row=1)
    sheet_name = "26ss アパレル１次spring1차스프링오픈(COLOR ONLY)"
    filter_func = lambda pi: pi["title"] not in EXCLUDE_APPAREL_TITLES
    client.sanity_check_sheet(sheet_name, product_inputs_filter_func=filter_func)

    scheduled_time = datetime.datetime(
        2026, 3, 10, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival", TAG],
        product_inputs_filter_func=filter_func,
        scheduled_time=scheduled_time
    )


def create_26ss_color_size():
    client = GbhClient(product_sheet_start_row=1)
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    sheet_name = "26ss アパレル１次spring1차스프링오픈(COLOR+SIZE)"
    filter_func = lambda pi: pi["title"] not in EXCLUDE_APPAREL_TITLES
    client.sanity_check_sheet(sheet_name, product_inputs_filter_func=filter_func)

    scheduled_time = datetime.datetime(
        2026, 3, 10, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival", TAG],
        product_inputs_filter_func=filter_func,
        scheduled_time=scheduled_time
    )


def main():
    create_26ss_color_only()
    create_26ss_color_size()


if __name__ == "__main__":
    main()
