import logging

logging.basicConfig(level=logging.INFO)

from brands.gbh.client import GbhClient, GbhClientColorOptionOnly
from brands.dev.client import dev_client


def create_26ss_color_size():
    client = dev_client(GbhClient())
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False

    sheet_name = "26ss アパレルpre-spring어패럴프리스프링오픈(COLOR+SIZE)"
    client.process_sheet_to_products(sheet_name, additional_tags=["New Arrival"])


def create_26ss_color_only():
    client = dev_client(GbhClientColorOptionOnly())

    sheet_name = "26ss アパレルpre-spring어패럴프리스프링오픈(COLOR ONLY)"
    client.process_sheet_to_products(sheet_name, additional_tags=["New Arrival"])


def main():
    create_26ss_color_only()
    create_26ss_color_size()


if __name__ == "__main__":
    main()
