import datetime
import logging
import zoneinfo
from brands.gbh.client import GbhClientColorOptionOnly, GbhCosmeticClient

logging.basicConfig(level=logging.INFO)

EXCLUDE_COSMETIC_TITLES = ["DEEP CLEANSING SHAMPOO", "BODY WASH NEROLI MUSK"]
TAG = "26SS_3.10"


def main():
    client = GbhCosmeticClient(
        product_sheet_start_row=1, remove_existing_new_product_indicators=False
    )
    sheet_name = "新コスメ(코스메신상)3/10open"
    filter_func = lambda pi: pi["title"] not in EXCLUDE_COSMETIC_TITLES
    client.sanity_check_sheet(sheet_name, product_inputs_filter_func=filter_func)

    scheduled_time = datetime.datetime(
        2026, 3, 10, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival", TAG],
        product_inputs_filter_func=filter_func,
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    main()
