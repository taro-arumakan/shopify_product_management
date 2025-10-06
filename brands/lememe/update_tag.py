# Recommend: 4
# New Arrivals -> 25 Fall & Winter

import logging
import utils

logging.basicConfig(level=logging.INFO)

tags_map = {
    "Best": "Recommend",
}


def main():
    client = utils.client("lememek")
    products = client.products_by_tag("Best")
    for product in products:
        tags = [tags_map.get(t, t) for t in product["tags"]]
        logging.info(f"updating {product['title']} from {product['tags']} to {tags}")
        client.update_product_tags(product["id"], ",".join(tags))


if __name__ == "__main__":
    main()
