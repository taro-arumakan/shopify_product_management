import logging

logging.basicConfig(level=logging.INFO)

import utils


titles = [
    "Egg wallet bag",
    "Fling bag",
    "Freckle fold bag",
    "Luv basket bag",
    "Luv lock duffle bag",
    "Luv moon bag",
    "Macaroon bag",
    "Ridge shoulder bag",
    "Clip rucksack",
    "Small fling bag",
    "Took bag (Leather)",
]
location_names = ["Archivépke Warehouse", "Envycube Warehouse"]


def main():
    client = utils.client("archive-epke")
    for title in titles:
        products = client.products_by_query(f"title:'{title}' AND status:'ACTIVE'")
        for product in products:
            for variant in product["variants"]["nodes"]:
                logging.info(f'activating {variant["sku"]} at {location_names}')
                client.enable_and_activate_inventory_by_sku(
                    variant["sku"], location_names
                )


if __name__ == "__main__":
    main()
