import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("gbh")
    for tag in ["24fall", "24 winter"]:
        products = client.products_by_tag(tag)
        products = [p for p in products if not any("25" in t for t in p["tags"])]
        for product in products:
            client.archive_product(product)


if __name__ == "__main__":
    main()
