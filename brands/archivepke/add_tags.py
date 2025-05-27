import utils

client = utils.client("archive-epke")
nylon_products = client.products_by_query(
    "tag:'Nylon bag'", additional_fields=["status"]
)
nylon_products = [p for p in nylon_products if p["status"] == "ACTIVE"]

took_products = client.products_by_query("title:*Took*", additional_fields=["status"])
took_products = [
    p
    for p in took_products
    if p["status"] == "ACTIVE" and p["title"] not in ["Took bag (Leather)"]
]

for p in nylon_products + took_products:
    new_tags = p["tags"] + ["2025_2Q_10%_Off"]
    client.update_product_tags(p["id"], ",".join(new_tags))
