import logging
import pprint
import string

import utils

SHOPNAME = "alvanas"
SHEET_TITLE = "Product Master"

start_row = 1
column_map = {
    "sku": string.ascii_uppercase.index("M"),
    "quantity": string.ascii_uppercase.index("N"),
}


def sku_quantity_map_from_sheet(shop_name, sheet_title):
    client = utils.client(shop_name)
    rows = client.worksheet_rows(client.sheet_id, sheet_title)

    res = {}
    for row in rows[1:]:
        assert (
            row[column_map["sku"]] not in res
        ), f"same sku found in multiple rows!!: {row}"
        if row[column_map["quantity"]]:
            res[row[column_map["sku"]]] = int(row[column_map["quantity"]])
    return res


def main():
    logging.basicConfig(level=logging.INFO)

    sku_quantity_map = sku_quantity_map_from_sheet(SHOPNAME, SHEET_TITLE)

    pprint.pprint(sku_quantity_map)
    client = utils.client(SHOPNAME)
    location_id = client.location_id_by_name("Jingumae")
    assert location_id, "location id not found"

    for sku, quantity in sku_quantity_map.items():
        res = client.set_inventory_quantity_by_sku_and_location_id(
            sku, location_id, quantity
        )
        logging.info(f"updated {sku} to {quantity}: {res}")


if __name__ == "__main__":
    main()
