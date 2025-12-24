import logging

logging.basicConfig(format="%(message)s", level=logging.INFO)

import pandas as pd
import utils

logging.getLogger("helpers.shopify_graphql_client.product_queries").setLevel(
    logging.WARNING
)

client = utils.client("gbh")
DRY_RUN = False


def sanitize_title(title: str) -> str:
    return " ".join(filter(None, title.split(" ")))


def existing_products_by_tag(tag: str):
    existing_products = client.products_by_tag(tag)
    return [p for p in existing_products if tag in p["tags"]]


def remove_existing_tag(tag: str, dry_run: bool = True):
    existing_products = existing_products_by_tag(tag)
    logging.info(f"--- Removing from {len(existing_products)} existing products ---")
    for product in existing_products:
        new_tags = [t for t in product["tags"] if t != tag]
        logging.info(f"{product['title']}")
        if not dry_run:
            client.update_product_tags(product["id"], ",".join(new_tags))


def add_tag(title: str, tag: str, dry_run: bool = True):
    product = client.product_by_title(title)
    new_tags = product["tags"] + [tag]
    logging.info(f"{product['title']}")
    if not dry_run:
        client.update_product_tags(product["id"], ",".join(new_tags))


def create_collection_by_tag(tag: str):
    collection = client.collection_create_by_tag(collection_title=tag, tag=tag)
    client.publish_by_product_or_collection_id(collection["id"])


def main():
    rows = client.worksheet_rows(
        sheet_id="10L3Rqrno6f4VZvJRHC5dvuZgVxKzTo3wK9KvB210JC0",
        sheet_title="カテゴリー変更",
    )
    tags = rows[0]
    df = pd.DataFrame(columns=tags, data=rows[1:])

    for tag in tags:
        logging.info(f"processing {tag}")
        if not DRY_RUN:
            create_collection_by_tag(tag)
        remove_existing_tag(tag, dry_run=DRY_RUN)

        titles = list(filter(None, df[tag]))
        logging.info(f"--- Adding to {len(titles)} products ---")
        for title in titles:
            title = sanitize_title(title)
            add_tag(title, tag, dry_run=DRY_RUN)
        print()


if __name__ == "__main__":
    main()
