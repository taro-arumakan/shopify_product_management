import logging
from brands.lememe.client import LememeClient


logging.basicConfig(level=logging.INFO)


def main():
    client = LememeClient()
    sheet_name = "Small Goods"
    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(sheet_name)


if __name__ == "__main__":
    main()
