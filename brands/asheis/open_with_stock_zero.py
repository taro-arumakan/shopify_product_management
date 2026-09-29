import utils


def original_inventoryQuantity_by_sku():
    return {
        "21263430302400": 30,
        "21263430302700": 20,
        "21263430290600": 48,
        "21263430292400": 38,
        "21263430292700": 27,
        "21263410230100": 40,
        "21263410232700": 35,
        "21263470372400": 35,
        "21263470372700": 15,
        "21263110372400": 45,
        "21263110372700": 30,
        "21263410372400": 40,
        "21263410372700": 35,
        "21263210151200": 13,
        "21263210152700": 25,
        "21263410225700": 28,
        "21263410222100": 47,
        "21263110131291": 4,
        "21263110131292": 1,
        "21263110132491": 7,
        "21263110132492": 3,
        "21263110132791": 7,
        "21263110132792": 3,
        "21263430342400": 38,
        "21263430342700": 25,
        "21263110142191": 10,
        "21263110142192": 4,
        "21263110142491": 17,
        "21263110142492": 7,
    }


def revert_stocks(dry_run=True):
    client = utils.client("ASHEIS")
    stock_by_sku = original_inventoryQuantity_by_sku()

    location_id = client.location_id_by_name(client.LOCATIONS[0])
    variants = client.variants_by_skus(stock_by_sku.keys())
    for v in variants:
        if not dry_run:
            client.set_inventory_quantity_by_sku_and_location_id(
                v["sku"], location_id, stock_by_sku[v["sku"]]
            )
        else:
            print(f"update {v['sku']} to {stock_by_sku[v['sku']]}")


def main():
    client = utils.client("ASHEIS")
    products = client.products_by_collection_handle("26_oct_1")
    ids = [p["id"].rsplit("/", 1)[-1] for p in products]
    products = client.products_by_query(" OR ".join(f"id:'{id}'" for id in ids))
    for p in products:
        for v in p["variants"]["nodes"]:
            print(f"'{v['sku']}': {v['inventoryQuantity']},")

    location_id = client.location_id_by_name(client.LOCATIONS[0])
    for p in products:
        for v in p["variants"]["nodes"]:
            client.set_inventory_quantity_by_sku_and_location_id(
                v["sku"], location_id, 0
            )
        client.publish_by_product_or_collection_id(p["id"])


if __name__ == "__main__":
    revert_stocks()
