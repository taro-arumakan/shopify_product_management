import datetime
import logging
import zoneinfo
import utils

logging.basicConfig(level=logging.INFO)

from brands.liberaiders.product_create import product_info_list_from_sheet


def main():
    client = utils.client("liberaiders")
    products = client.products_by_query("status:'DRAFT'")
    for product in products:
        client.activate_and_publish_by_product_id(product["id"])


if __name__ == "__main__":
    main()
