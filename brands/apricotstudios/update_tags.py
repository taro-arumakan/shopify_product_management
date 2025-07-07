import logging
import pprint
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("apricot-studios")
    products = client.products_by_tag("2025_sale_event")
    for p in products:
        new_tags = p["tags"] + ["Special Summer Sale"]
        print(["title"], new_tags)
        pprint.pprint(client.update_product_tags(p["id"], ",".join(new_tags)))


if __name__ == "__main__":
    main()
