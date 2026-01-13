import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("blossomhcompany")

    products = client.products_by_tag("SHOES")
    for product in products:
        client.update_product_theme_template(product["id"], "shoes")


if __name__ == "__main__":
    main()
