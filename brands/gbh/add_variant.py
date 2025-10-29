import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("gbhjapan")
    product_info_list = client.product_info_list_from_sheet("APPAREL 25FW (WINTER 1次)")
    product_info = product_info_list[0]
    client.add_variants_from_product_info(product_info)


if __name__ == "__main__":
    main()
