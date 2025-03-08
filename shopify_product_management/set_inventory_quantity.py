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

def sku_quantity_map_from_sheet():
    sheet_index = get_sheet_index_by_title(GOOGLE_CREDENTIAL_PATH, GSPREAD_ID, SHEET_TITLE)
    logger.info(f'sheet index of {SHEET_TITLE} is {sheet_index}')
    worksheet = gspread_access(GOOGLE_CREDENTIAL_PATH).open_by_key(GSPREAD_ID).get_worksheet(sheet_index)
    rows = worksheet.get_all_values()

    # start_row 1 base, columns are 0 base
    status_index = 1
    sku_index = 18
    quantity_index = 19

    start_row = None
    for i, row in enumerate(rows):
        if row[status_index].startswith('3/10'):
            logger.info(f'starting at row {i}')
            start_row = i
            break
    res = {}
    for row in rows[start_row:]:
        if row[status_index] and not row[status_index].startswith('3/10'):
            logger.info(f'breaking at row: {row}')
            break
        assert row[sku_index] not in res, f'same sku found in multiple rows!!: {row[sku_index]}'
        res[row[sku_index]] = int(row[quantity_index])
    return res


def main():

    skip_skus = ['KM-24FW-TS02-IV-S', 'KM-24FW-TS02-IV-M']
    sku_quantity_map = sku_quantity_map_from_sheet()
    import pprint
    pprint.pprint(sku_quantity_map)
    location_id = location_id_by_name(SHOPNAME, ACCESS_TOKEN, 'KUME warehouse')
    assert location_id, 'location id not found'
    for sku, quantity in sku_quantity_map.items():
        if sku in skip_skus:
            logger.info(f'skipping update of {sku}')
        else:
          res = set_inventory_quantity_by_sku_and_location_id(SHOPNAME, ACCESS_TOKEN, sku, location_id, quantity)
          logger.info(f'updated {sku} to {quantity}: {res}')


if __name__ == '__main__':
    main()