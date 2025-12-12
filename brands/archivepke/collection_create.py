import logging
import utils

logging.basicConfig(level=logging.INFO)

skus = [
    "OVBAX25002MCB",
    "OVBAX25002BLK",
    "OVBAX25001BLK",
    "OVBAX25201GBG",
    "OVBAX25201GCB",
    "OVBAX25201GCM",
    "OVBAX25213GBG",
    "OVBAX25213GCB",
    "OVBAX25212BLK",
    "OVBAX25212SCM",
    "OVBAX25211BLK",
    "OVBAX25211MCB",
    "OVBAX25228BLK",
    "OVBAX25228OLG",
    "OVBTX25202BLK",
    "OVBTX25202DKB",
]


def main():
    client = utils.client("archive-epke")
    product_ids = {client.product_id_by_sku(sku) for sku in skus}
    client.collection_create_by_product_ids("2025 POP-UP 15% OFF", product_ids)


if __name__ == "__main__":
    main()
