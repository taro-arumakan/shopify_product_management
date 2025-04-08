from shopify_graphql_client.client import ShopifyGraphqlClient
from dotenv import load_dotenv
from shopify_product_management.google_utils import gspread_access, get_sheet_index_by_title
import os


def main():
    load_dotenv(override=True)
    shop_name = 'archive-epke'
    access_token = os.getenv('ACCESS_TOKEN')
    google_credential_path = os.getenv('GOOGLE_CREDENTIAL_PATH')

    sheet_id = '18YPrX-1CqvAxmrE1P6jrtmewkKZtiInngQw2bOTacWg'
    sheet_name = '2025.4/10 Release'

    sgc = ShopifyGraphqlClient(shop_name, access_token)

    sheet_index = get_sheet_index_by_title(google_credential_path, sheet_id, sheet_name)
    worksheet = gspread_access(google_credential_path).open_by_key(sheet_id).get_worksheet(sheet_index)
    rows = worksheet.get_all_values()

    for row in rows[2:]:
        title = row[3]
        print(title)
        try:
            gid = sgc.product_by_title(title)
        except RuntimeError as e:
            print(e)
        else:
            print(gid)

if __name__ == '__main__':
    main()