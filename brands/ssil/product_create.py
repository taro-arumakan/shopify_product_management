import logging
from brands.ssil.client import SsilClient

logging.basicConfig(level=logging.INFO)


def main():

    c = SsilClient()
    product_info_list = c.product_info_list_from_sheet(
        "material & size options (rings etc)"
    )
    # for i, product_info in enumerate(product_info_list):
    #     if product_info["title"] == "Lucky Clover Drop R_WG":
    #         break
    # product_info_list = product_info_list[i:]
    c.sanity_check_product_info_list(product_info_list)
    for product_info in product_info_list:
        c.create_a_product(product_info)
        c.process_product_images(product_info)
    c.update_stocks(product_info_list)
    c.publish_products(product_info_list)


if __name__ == "__main__":
    main()
