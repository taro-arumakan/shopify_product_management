import logging
import utils
from brands.blossom.client import BlossomClient

logging.basicConfig(level=logging.INFO)

skus = [
    "BC2601SPPT005-01-GR-XS",
    "BC2601SPPT005-01-GR-S",
    "BC2601SPPT005-01-GR-M",
    "BC2602SPBL004-01-GR-S",
    "BC2602SPBL004-01-GR-M",
    "BC2601SPSK001-01-GR-XS",
    "BC2601SPSK001-01-GR-S",
    "BC2601SPSK001-01-GR-M",
    "BC2601SPBL002-01-IV-S",
    "BC2601SPBL002-01-IV-M",
    "BC2601SPBL002-01-GR-S",
    "BC2601SPBL002-01-GR-M",
    "BC2601SPBL002-01-KB-S",
    "BC2601SPBL002-01-KB-M",
    "BC2601SPBL002-01-BK-S",
    "BC2601SPBL002-01-BK-M",
    "BC2601SPCT001-01-GR-S",
    "BC2601SPCT001-01-GR-M",
    "BC2601SPCT001-01-KB-S",
    "BC2601SPCT001-01-KB-M",
    "BC2601SPCT001-01-BK-S",
    "BC2601SPCT001-01-BK-M",
]


def main():
    client = BlossomClient()
    product_ids = {client.product_id_by_sku(sku) for sku in skus}
    client.collection_create_by_product_ids("26SS drop3", product_ids)


if __name__ == "__main__":
    main()
