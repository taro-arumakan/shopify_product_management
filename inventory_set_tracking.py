import pprint
import string
import utils


def main():

    shop_name = 'archive-epke'
    sheet_name = '2025.4/10 Release'
    client = utils.client(shop_name)
    rows = client.worksheet_rows(client.sheet_id, sheet_name)

    location_names = ['Archivépke Warehouse', 'Envycube Warehouse']
    aw_location_id = client.location_id_by_name(location_names[0])

    for row in rows[2:]:
        sku = row[string.ascii_lowercase.index('e')]
        print(sku)
        res = client.enable_and_activate_inventory(sku, location_names)
        pprint.pprint(res)
        quantity = int(row[string.ascii_lowercase.index('m')])
        res = client.set_inventory_quantity_by_sku_and_location_id(sku, aw_location_id, quantity)
        pprint.pprint(res)

if __name__ == '__main__':
    main()
