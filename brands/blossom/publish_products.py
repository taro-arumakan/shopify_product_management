import logging
import utils


logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("blossomhcompany")
    products = client.products_by_collection_id(443130380539)
    for product in products:
        client.activate_and_publish_by_product_id(product["id"])


if __name__ == "__main__":
    main()
