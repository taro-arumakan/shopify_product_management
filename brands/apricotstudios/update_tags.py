import logging
from brands.apricotstudios.client import ApricotStudiosClient

logging.basicConfig(level=logging.INFO)


def main():
    client = ApricotStudiosClient()
    products = client.products_by_query()
    for product in products:
        current_tags = product.get("tags", [])
        normalized_tags = [client.normalize_tag(tag) for tag in current_tags if tag]
        logging.info(f"normalizing tags: {product['title']}")
        client.update_product_tags(product["id"], ",".join(normalized_tags))
    logging.info(f"done. normalized {len(products)} products")


if __name__ == "__main__":
    main()
