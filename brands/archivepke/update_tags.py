import utils

client = utils.client("archive-epke")
rows = client.worksheet_rows(
    "1fGXTDfe10F4hBG08JG5tj4Ae4bKgXtJtJYWJnPTUd4w", "On sale tab list"
)

variants = [client.variant_by_sku(row[5]) for row in rows[2:18]]
product_ids = set(v["product"]["id"] for v in variants)

for product_id in product_ids:
    product = client.product_by_id(product_id)
    tags = product["tags"]
    tags.append("on_sale")
    print(product_id, tags)
    client.update_product_tags(product_id, tags)
