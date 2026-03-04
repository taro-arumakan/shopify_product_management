import logging
from brands.gbh.client import GbhClient, GbhClientColorOptionOnly, GbhCosmeticClient

logging.basicConfig(level=logging.INFO)

EXCLUDE_APPAREL_TITLES = ["GARDEN BAG SMALL", "TULIP BAG"]
EXCLUDE_COSMETIC_TITLES = ["DEEP CLEANSING SHAMPOO", "BODY WASH NEROLI MUSK"]


def archive_apparel_products():
    client = GbhClient()
    for title in EXCLUDE_APPAREL_TITLES:
        product = client.product_by_title(title)
        client.archive_product(product)


def archive_cosmetic_products():
    client = GbhClient()
    for title in EXCLUDE_COSMETIC_TITLES:
        product = client.product_by_title(title)
        client.archive_product(product)


def create_26ss_color_only():
    client = GbhClientColorOptionOnly(product_sheet_start_row=1)
    sheet_name = "26ss アパレル１次spring1차스프링오픈(COLOR ONLY)"
    filter_func = lambda pi: pi["title"] not in EXCLUDE_APPAREL_TITLES
    client.sanity_check_sheet(sheet_name, product_inputs_filter_func=filter_func)
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival"]
    )


def create_26ss_color_size():
    client = GbhClient(product_sheet_start_row=1)
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    sheet_name = "26ss アパレル１次spring1차스프링오픈(COLOR+SIZE)"
    filter_func = lambda pi: pi["title"] not in EXCLUDE_APPAREL_TITLES
    client.sanity_check_sheet(sheet_name, product_inputs_filter_func=filter_func)
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival"]
    )


def create_cosmetic():
    client = GbhCosmeticClient(product_sheet_start_row=1)
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    sheet_name = "新コスメ(코스메신상)3/10open"
    filter_func = lambda pi: pi["title"] not in EXCLUDE_COSMETIC_TITLES
    client.sanity_check_sheet(sheet_name, product_inputs_filter_func=filter_func)
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival"]
    )


def main():
    archive_apparel_products()
    archive_cosmetic_products()
    create_26ss_color_only()
    create_26ss_color_size()
    create_cosmetic()


if __name__ == "__main__":
    main()
