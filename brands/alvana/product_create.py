import logging
from brands.alvana.client import AlvanaClient

logging.basicConfig(level=logging.INFO)


def main():

    c = AlvanaClient()
    product_info_list = c.product_info_list_from_sheet("25AW 20251022")
    c.sanity_check_product_info_list(product_info_list)
    product_ids = []
    for product_info in product_info_list:
        product_ids.append(c.create_a_product(product_info))
        c.process_product_images(product_info)
    c.update_stocks(product_info_list)
    for product_id in product_ids:
        c.activate_and_publish_by_product_id(product_id)


if __name__ == "__main__":
    main()
