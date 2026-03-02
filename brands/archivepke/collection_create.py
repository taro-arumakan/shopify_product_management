import logging
import utils

logging.basicConfig(level=logging.INFO)

skus = [
    "OVBAX26051GBK",
    "OVBAX26051GGR",
    "OVBAX26052GBK",
    "OVBAX26052SCR",
    "OVBAX26053BLK",
    "OVBAX26053IGR",
    "OVBAX26055BLK",
    "OVBAX26055CMI",
    "OVBAX26055OBG",
    "OVBSX26055BLK",
    "OVBSX26154BLK"
]


def main():
    client = utils.client("archive-epke")
    product_ids = {client.product_id_by_sku(sku) for sku in skus}
    client.collection_create_by_product_ids("26SS NEW COLOR 15% PROMOTION", product_ids)


if __name__ == "__main__":
    main()
