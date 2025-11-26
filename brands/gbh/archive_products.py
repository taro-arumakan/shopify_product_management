import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("gbh")
    products = client.products_by_query(
        f"tag:*24* AND tag:'APPAREL' AND status:'ACTIVE'"
    )
    for product in products:
        if "25FW" not in product["tags"]:
            client.archive_product(product)


if __name__ == "__main__":
    main()
