import logging
import os

from dotenv import load_dotenv
from google_utils import get_sheet_index_by_title, gspread_access
from shopify_utils import location_id_by_name, set_inventory_quantity_by_sku_and_location_id

load_dotenv(override=True)
SHOPNAME = 'kumej'
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
print(ACCESS_TOKEN)
GOOGLE_CREDENTIAL_PATH = os.getenv('GOOGLE_CREDENTIAL_PATH')

GSPREAD_ID = '1buFubQ6Ng4JzYn4JjTsv8SQ2J1Qgv1yyVrs4yQUHfE0'
SHEET_TITLE = '25ss'

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

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


def sku_quantity_map_from_sheet():
    sheet_index = get_sheet_index_by_title(GOOGLE_CREDENTIAL_PATH, GSPREAD_ID, SHEET_TITLE)
    logger.info(f'sheet index of {SHEET_TITLE} is {sheet_index}')
    worksheet = gspread_access(GOOGLE_CREDENTIAL_PATH).open_by_key(GSPREAD_ID).get_worksheet(sheet_index)
    rows = worksheet.get_all_values()

    columns = column_map(SHOPNAME)

    res = {}
    for row in rows[columns['start_row']:]:
        assert row[columns['sku_index']] not in res, f'same sku found in multiple rows!!: {row}'
        if not row[1].startswith('3/31'):
            logger.info(f'skipping row: {row[0]} {row[1]}')
        else:
            res[row[columns['sku_index']]] = int(row[columns['quantity_index']])
    return res


def main():

    skip_skus = ['KM-24FW-TS02-IV-S', 'KM-24FW-TS02-IV-M']
    sku_quantity_map = sku_quantity_map_from_sheet()
    import pprint
    pprint.pprint(sku_quantity_map)
    location_id = location_id_by_name(SHOPNAME, ACCESS_TOKEN, 'KUME Warehouse')
    assert location_id, 'location id not found'
    for sku, quantity in sku_quantity_map.items():
        if sku in skip_skus:
            logger.info(f'skipping update of {sku}')
        else:
          res = set_inventory_quantity_by_sku_and_location_id(SHOPNAME, ACCESS_TOKEN, sku, location_id, quantity)
          logger.info(f'updated {sku} to {quantity}: {res}')


if __name__ == '__main__':
    main()
