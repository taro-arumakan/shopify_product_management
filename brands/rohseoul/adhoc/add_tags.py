import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("rohseoul")
    products = client.products_by_tag("2025-10-24")
    for product in products:
        tags = product["tags"]
        tags += ["25-fw-3rd"]
        client.update_product_tags(product["id"], ",".join(tags))


if __name__ == "__main__":
    main()
