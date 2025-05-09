import utils

client = utils.client("kumej")
products = client.products_by_query("tag:'new'")
news = [product for product in products if "'new'" in product["tags"]]

for n in news:
    new_tags = ["New Arrival" if tag == "'new'" else tag for tag in n["tags"]]
    client.update_product_tags(n["id"], ",".join(new_tags))
