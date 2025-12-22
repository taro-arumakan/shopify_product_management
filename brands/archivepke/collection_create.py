import logging
import utils

logging.basicConfig(level=logging.INFO)

skus = [
    "OVBAX26008PDB",
    "OVBAX26007SDB",
    "OVBAX26007SAL",
    "OVBAX25210SCR",
    "OVBAX25004BLK",
    "OVBAX25001BLK",
    "OVBAX25002BLK",
    "OVBAX25010BLK",
    "OVBAX25102BLK",
    "OVBAX25005BLK",
    "OVBAX25012SDB",
]


def main():
    client = utils.client("archive-epke")
    product_ids = {client.product_id_by_sku(sku) for sku in skus}
    client.collection_create_by_product_ids("25 Christmas promotion", product_ids)


if __name__ == "__main__":
    main()
