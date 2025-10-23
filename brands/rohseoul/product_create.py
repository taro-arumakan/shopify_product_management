import logging
from brands.rohseoul.client import RohseoulClient

logging.basicConfig(level=logging.INFO)


def main():
    handle_suffix = "25fw-3rd"

    client = RohseoulClient()
    product_info_list = client.product_info_lists_from_sheet(
        sheet_name="25FW WINTER - copy", handle_suffix=handle_suffix
    )
    client.sanity_check_product_info_list(product_info_list)
    for product_info in product_info_list:
        client.create_a_product(product_info)
        client.process_product_images(product_info, handle_suffi=handle_suffix)
    client.update_stocks(product_info_list)
    client.publish_products(product_info_list)


if __name__ == "__main__":
    main()
