import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("alvanas")
    product_inputs = client.product_inputs_by_sheet_name("Product Master")

    for product_input in product_inputs:
        title = product_input["title"]
        weight = product_input.get("weight")
        if weight:
            product = client.product_by_title(title)
            skus = [v["sku"] for v in product["variants"]["nodes"]]
            for sku in skus:
                client.update_inventory_item_weight_by_sku(
                    sku, weight, unit="KILOGRAMS"
                )


if __name__ == "__main__":
    main()
