import logging

logging.basicConfig(level=logging.INFO)

from brands.rohseoul.client import RohseoulClient
from brands.dev.client import dev_client


def main():
    client = dev_client(RohseoulClient(product_sheet_start_row=2))
    sheet_name = "CO as NEW"
    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(sheet_name)


if __name__ == "__main__":
    main()
