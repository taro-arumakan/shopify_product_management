import logging
from itertools import islice

logging.basicConfig(level=logging.INFO)

import utils


def main():
    client = utils.client("blossom")
    client.sheet_id = "1UiTRsJrco5IHEXEaTVfzGiUFRB20ykVEYbMZtqhyGQ8"
    rows = client.worksheet_rows(
        sheet_id="1UiTRsJrco5IHEXEaTVfzGiUFRB20ykVEYbMZtqhyGQ8", sheet_title="シート1"
    )
    skus = iter(r[0] for r in rows[1:])
    product_ids = set()
    while True:
        chunk = list(islice(skus, 100))
        if not chunk:
            break
        variants = client.product_variants_by_query(
            " OR ".join(f"sku:'{sku}'" for sku in chunk)
        )
        print(len(variants))
        product_ids.update([v["product"]["id"] for v in variants])
        print(len(product_ids))
    products = client.products_by_query(
        " OR ".join(f"id:'{i.rsplit('/', 1)[-1]}'" for i in product_ids)
    )
    print(len(products))
    for product in products:
        tags = product["tags"] + ["25FW"]
        logging.info(f"updating {product['title']}: {",".join(tags)}")
        client.update_product_tags(product["id"], ",".join(tags))


if __name__ == "__main__":
    main()
