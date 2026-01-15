import logging
import utils

logging.basicConfig(level=logging.INFO)

skus = [
    "OVBAX25004BLK",
    "OVBAX25005BLK",
    "OVBAX25229DKB",
    "OVBAX26004SBK",
    "OVBAX26004SCR",
    "OVBAX25115BLK",
    "OVBRX25102BLK",
]


def main():
    client = utils.client("archive-epke")
    product_ids = {client.product_id_by_sku(sku) for sku in skus}
    client.collection_create_by_product_ids("26 New Year Appreciation Promotion", product_ids)


if __name__ == "__main__":
    main()
