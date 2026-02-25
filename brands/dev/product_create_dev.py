import logging

logging.basicConfig(level=logging.INFO)

from brands.gbh.client import GbhClient, GbhClientColorOptionOnly
from brands.dev.client import dev_client


def archive():
    client = dev_client(GbhClient())
    product = client.product_by_title("MID RISE REGULAR FIT JEANS")
    client.archive_product(product)


def recreate():
    client = dev_client(GbhClient(product_sheet_start_row=1))
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False

    sheet_name = "26ss アパレルpre-spring어패럴프리스프링오픈(COLOR+SIZE)"
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival"],
        product_inputs_filter_func=lambda pi: pi["title"]
        in ["MID RISE REGULAR FIT JEANS"],
    )


def main():
    archive()
    recreate()


if __name__ == "__main__":
    main()
