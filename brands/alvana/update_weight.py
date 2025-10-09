import logging
import utils
from brands.alvana.product_create import product_info_list_from_sheet

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("alvanas")
    product_info_list = product_info_list_from_sheet(
        client, client.sheet_id, "Product Master"
    )
    for product_info in product_info_list:
        title = product_info["title"]
        weight = product_info.get("weight")
        if weight:
            product = client.product_by_title(title)
            skus = [v["sku"] for v in product["variants"]["nodes"]]
            for sku in skus:
                client.update_inventory_item_weight_by_sku(
                    sku, weight, unit="KILOGRAMS"
                )


if __name__ == "__main__":
    main()
