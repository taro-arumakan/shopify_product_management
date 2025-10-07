collection_id = "447036784861"
skus = [
    "OVBAX25012SDB",
    "OVBAX25036SDB",
    "OVBAX25036SAL",
    "OVBAX25203SAL",
    "OVBAX25212SCM",
    "OVBAX25004SDB",
]

import utils
import logging

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("archive-epke")
    product_ids = [client.product_id_by_sku(sku) for sku in skus]
    client.collection_add_products(collection_id, product_ids)


if __name__ == "__main__":
    main()
