import utils

client = utils.client("kumej")
products = client.products_by_query("tag:'DRESSES'")

for p in products:
    new_tags = ["DRESS" if tag == "DRESSES" else tag for tag in p["tags"]]
    client.update_product_tags(p["id"], ",".join(new_tags))
