import logging
from brands.blossom.client import BlossomClientBags


logging.basicConfig(level=logging.INFO)


def main():
    sheet_name = "bags"
    client = BlossomClientBags()
    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(
        "bags", additional_tags=["25_winter", "New Arrival"]
    )


if __name__ == "__main__":
    main()
