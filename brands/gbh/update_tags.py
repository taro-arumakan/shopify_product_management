import utils

client = utils.client("gbh")
products = client.products_by_query(
    "tag_not:'APPAREL' AND tag_not:'HOME' AND tag_not:'COSMETICS'"
)
for product in products:
    tags = product["tags"] + ["APPAREL"]
    client.update_product_tags(product["id"], ",".join(tags))
