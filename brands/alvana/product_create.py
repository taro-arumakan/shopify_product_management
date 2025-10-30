import logging
from brands.alvana.client import AlvanaClient

logging.basicConfig(level=logging.INFO)


def main():

    client = AlvanaClient()
    product_info_list = client.product_info_list_from_sheet(
        "25AW Product Master - cloned"
    )
    product_info_list = [
        pi for pi in product_info_list if pi["title"] == "5G LAMS WOOL CREW KNIT"
    ]
    for pi in product_info_list:
        client.create_product_from_product_info(pi)
        client.process_product_images(pi)
    client.update_stocks(product_info_list)
    client.publish_products(product_info_list, scheduled_time=None)


if __name__ == "__main__":
    main()
