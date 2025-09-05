import utils

client = utils.client("lememek")
products = client.products_by_collection_handle("all")

for product in products:
    product = client.product_by_id(product["id"], additional_fields=["descriptionHtml"])
    desc = product["descriptionHtml"]
    desc = desc.replace("<th>素材</th>", "<td>素材</td>").replace(
        "<th>原産国</th>", "<td>原産国</td>"
    )
    client.update_product_description(desc=desc, product_id=product["id"])
