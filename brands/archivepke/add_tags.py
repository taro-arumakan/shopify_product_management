import logging
import utils

logging.basicConfig(level=logging.INFO)

skus = [
    "OVBAX25010BLK",
    "OVBAX25012SDB",
    "OVBAX25102BLK",
    #  'OVBAX25102IVO',
    "OVBRX25101BLK",
    "OVBRX25101DKB",
    "OVBRX25101BTT",
    "OVBAX25103BLK",
    "OVBAX24608IVO",
    "OVBAX24108NBE",
    "OVBAX25011BLK",
    "OVBAX25301GYD",
    "OVBAX25210SCR",
    "OVBAX25036SAL",
    "OVBAX25036SDB",
]


client = utils.client("archive-epke")
for sku in skus:
    product_id = client.product_id_by_sku(sku)
    product = client.product_by_id(product_id)
    tags = product["tags"]
    tags += ["202508_secret_sale"]
    client.update_product_tags(product_id, ",".join(tags))
