import logging
from brands.blossom.client import BlossomClientShoes

logging.basicConfig(level=logging.INFO)


def main():
    client = BlossomClientShoes
    sheet_name = "shoes"
    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(
        sheet_name, additional_tags=["25_drop4", "New Arrival"]
    )


if __name__ == "__main__":
    main()
