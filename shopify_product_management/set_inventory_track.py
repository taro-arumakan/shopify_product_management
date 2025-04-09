from shopify_graphql_client.client import ShopifyGraphqlClient
from google_utils import get_rows
import string

def main():
    from dotenv import load_dotenv
    import os
    import pprint

    load_dotenv(override=True, dotenv_path='.env')
    shop_name = 'archive-epke'
    access_token = os.getenv(f'{shop_name}-ACCESS_TOKEN')
    sgc = ShopifyGraphqlClient(shop_name, access_token)

    sheet_id = os.getenv(f'{shop_name}-GSPREAD_ID')
    sheet_name = '2025.4/10 Release'
    google_credential_path = os.getenv('GOOGLE_CREDENTIAL_PATH')

    rows = get_rows(google_credential_path, sheet_id=sheet_id, sheet_name=sheet_name)

    location_names = ['Archivépke Warehouse', 'Envycube Warehouse']
    for row in rows[2:]:
        sku = row[string.ascii_lowercase.index('e')]
        print(sku)
        res = sgc.enable_and_activate_inventory(sku, location_names)
        pprint.pprint(res)


if __name__ == '__main__':
    main()
