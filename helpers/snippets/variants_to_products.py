import logging
import utils


def main():
    logging.basicConfig(level=logging.INFO)
    titles = [
        "flower Lace Mini Skirt",
    ]
    client = utils.client("kumej")
    for product_title in titles:
        client.product_variants_to_products(product_title)


if __name__ == "__main__":
    main()
