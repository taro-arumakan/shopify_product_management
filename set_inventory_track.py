import pprint
import string
import google_api_interface
import shopify_graphql_client


def main():

    shop_name = 'archive-epke'
    sheet_name = '2025.4/10 Release'
    gai = google_api_interface.get(shop_name)
    rows = gai.worksheet_rows(gai.sheet_id, sheet_name)

    sgc = shopify_graphql_client.get(shop_name)

    location_names = ['Archivépke Warehouse', 'Envycube Warehouse']
    aw_location_id = sgc.location_id_by_name(location_names[0])

    for row in rows[2:]:
        sku = row[string.ascii_lowercase.index('e')]
        print(sku)
        res = sgc.enable_and_activate_inventory(sku, location_names)
        pprint.pprint(res)
        quantity = int(row[string.ascii_lowercase.index('m')])
        res = sgc.set_inventory_quantity_by_sku_and_location_id(sku, aw_location_id, quantity)
        pprint.pprint(res)

if __name__ == '__main__':
    main()
