import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("lememek")
    products = client.products_by_metafield("custom", "badges", "NEW")
    for product in products:
        client.update_badges_metafield(product["id"], [])

    products = client.products_by_tag("25FW")
    for product in products:
        client.update_badges_metafield(product["id"], ["NEW"])


if __name__ == "__main__":
    main()
