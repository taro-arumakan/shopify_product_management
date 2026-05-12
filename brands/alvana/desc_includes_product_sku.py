import utils

client = utils.client("alvana")


def run():
    products = client.products_by_query(additional_fields=["descriptionHtml"])

    for product in products:
        desc = product["descriptionHtml"]
        product_sku = product["variants"]["nodes"][0]["sku"].rsplit("-", 2)[0]
        if f"<td>{product_sku}</td>" in desc:
            continue
        if f"{product_sku}<br>" in desc:
            desc = desc.replace(f"{product_sku}<br>", "")
        desc = desc.replace(
            "</tbody>", f"<tr>\n<th>品番</th>\n<td>{product_sku}</td>\n</tr>\n</tbody>"
        )
        client.update_product_description(product["id"], desc)


def check_sku():
    products = client.products_by_query()

    for product in products:
        print(f"checking {product['title']}")
        for variant in product["variants"]["nodes"]:
            if not variant["sku"]:
                print(variant["displayName"])


if __name__ == "__main__":
    run()
