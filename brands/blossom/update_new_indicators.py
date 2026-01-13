import json
import logging
import utils

logging.basicConfig(level=logging.INFO)


def update_tags(client, product):
    tags = product["tags"] + ["New Arrival"]
    client.update_product_tags(product["id"], tags)


def update_badges(client, product):
    badges = [m for m in product["metafields"]["nodes"] if m["key"] == "badges"][0][
        "value"
    ]
    badges = json.loads(badges) + ["NEW"]
    client.update_badges_metafield(product["id"], badges)


def main():
    client = utils.client("blossomhcompany")

    products = client.products_by_tag("drop9")
    for product in products:
        update_tags(client, product)
        update_badges(client, product)


if __name__ == "__main__":
    main()
