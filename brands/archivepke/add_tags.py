import logging
import utils

logging.basicConfig(level=logging.INFO)

skus = [
    "OVBAX25032SWB",
    "OVBAX25027PBK",
    "OVBAX25027LKK",
    "OVBAX25027SBL",
    "OVBRX25005BLK",
    "OVBRX25005COC",
    "OVBAX25034SWB",
    "OVBAX25034SWK",
    "OVBAX25028BLK",
    "OVBAX25028COC",
    "OVBSX25106BEE",
    "OVBSX25106GRM",
    "OVBSX25105BEE",
    "OVBSX25105GRM",
    "OVBAX25107BLK",
    "OVBAX25107BEE",
    "OVBAX25107GRM",
    "OVBTX25002BLK",
    "OVBTX25002COC",
    "OVBSX25103BEE",
    "OVBSX25104BEE",
    "OVBSX25007BLK",
    "OVBSX25007LKK",
]

client = utils.client("archive-epke")
for sku in skus:
    product_id = client.product_id_by_sku(sku)
    product = client.product_by_id(product_id)
    tags = product["tags"]
    tags += ["summer_season_sale"]
    client.update_product_tags(product_id, ",".join(tags))
