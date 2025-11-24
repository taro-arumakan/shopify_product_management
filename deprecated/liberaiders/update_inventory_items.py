import logging
import utils

logging.basicConfig(level=logging.INFO)

client = utils.client("liberaiders")

titles = ["ALL CONDITIONS 3LAYER JACKET III", "UTILITY DOWN JACKET"]
weights = [0.6, 1.5]

for weight, title in zip(weights, titles):
    product = client.product_by_title(title)
    variants = product["variants"]["nodes"]

    for v in variants:
        client.enable_and_activate_inventory_by_sku(v["sku"], ["Shop Location"])
        client.update_inventory_item_weight_by_sku(v["sku"], weight)
