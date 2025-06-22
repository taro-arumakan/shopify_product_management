import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("archive-epke")
    products = client.products_by_collection_handle("took-bag")
    products += client.products_by_collection_handle("standard-line")

    product_ids = [product["id"] for product in products]
    client.collection_create("Sunny Essentials Sale", product_ids)


if __name__ == "__main__":
    main()
