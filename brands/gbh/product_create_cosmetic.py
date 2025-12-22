import datetime
import logging
import zoneinfo
from brands.gbh.client import GbhClientColorOptionOnly, GbhCosmeticClient

logging.basicConfig(level=logging.INFO)


def main():

    client = GbhCosmeticClient()
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    sheet_name = "新コスメ(코스메신상)"

    client.sanity_check_sheet(sheet_name)

    client.process_sheet_to_products(
        sheet_name, additional_tags=["New Arrival"]
    )


if __name__ == "__main__":
    main()
