import datetime
import logging
import zoneinfo
from brands.gbh.client import GbhClientColorOptionOnly, GbhCosmeticClient

logging.basicConfig(level=logging.INFO)

EXCLUDE_COSMETIC_TITLES = ["DEEP CLEANSING SHAMPOO", "BODY WASH NEROLI MUSK"]

def main():
    client = GbhCosmeticClient(product_sheet_start_row=1)
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    sheet_name = "新コスメ(코스메신상)3/10open"
    filter_func = lambda pi: pi["title"] not in EXCLUDE_COSMETIC_TITLES
    client.sanity_check_sheet(sheet_name, product_inputs_filter_func=filter_func)
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival"],
        product_inputs_filter_func=filter_func
    )


if __name__ == "__main__":
    main()
