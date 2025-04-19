import logging
import pprint

import utils

SHOPNAME = 'kumej'
SHEET_TITLE = '25ss'

# start_row 0 base, columns are 0 base
arhivepke_column_map = dict(
    sku_index = 4,
    quantity_index = 12,
    start_row = 3
)
kume_column_map = dict(
    sku_index = 18,
    quantity_index = 19,
    start_row = 3
)

def column_map(shop_name):
    if shop_name == 'archive-epke':
        return arhivepke_column_map
    elif shop_name == 'kumej':
        return kume_column_map
    else:
        raise ValueError(f'unsupported shop name: {shop_name}')


def sku_quantity_map_from_sheet(shop_name, sheet_title):
    client = utils.client(shop_name)
    rows = client.worksheet_rows(client.sheet_id, sheet_title)

    columns = column_map(shop_name)

    res = {}
    for row in rows[columns['start_row']:]:
        assert row[columns['sku_index']] not in res, f'same sku found in multiple rows!!: {row}'
        if not row[1].startswith('3/31'):
            logging.info(f'skipping row: {row[0]} {row[1]}')
        else:
            res[row[columns['sku_index']]] = int(row[columns['quantity_index']])
    return res


def main():
    logging.basicConfig(level=logging.INFO)

    skip_skus = ['KM-24FW-TS02-IV-S', 'KM-24FW-TS02-IV-M']
    sku_quantity_map = sku_quantity_map_from_sheet(SHOPNAME, SHEET_TITLE)

    pprint.pprint(sku_quantity_map)
    client = utils.client(SHOPNAME)
    location_id = client.location_id_by_name('KUME Warehouse')
    assert location_id, 'location id not found'

    for sku, quantity in sku_quantity_map.items():
        if sku in skip_skus:
            logging.info(f'skipping update of {sku}')
        else:
            res = client.set_inventory_quantity_by_sku_and_location_id(sku, location_id, quantity)
            logging.info(f'updated {sku} to {quantity}: {res}')


if __name__ == '__main__':
    main()
