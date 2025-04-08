from shopify_graphql_client.client import ShopifyGraphqlClient
import google_utils

def main():
    from dotenv import load_dotenv
    import os
    load_dotenv(override=True)
    shop_name = 'rawrowr'
    access_token = os.getenv("ACCESS_TOKEN")
    google_credential_path = os.getenv('GOOGLE_CREDENTIAL_PATH')
    sheet_id = '1AAW8HHGUER7t77k1I3Q4UghfrVG9kti5uuYKaTJvN2w'
    sheet_name = '20250211_v3'
    rows = google_utils.get_rows(google_credential_path, sheet_id, sheet_name)
    import string
    title_col = string.ascii_lowercase.index('b')
    sku_col = string.ascii_lowercase.index('q')
    sgc = ShopifyGraphqlClient(shop_name, access_token)
    print(len(rows))
    for row in rows[2:]:
        title =row[title_col]
        if title:
            sku = row[sku_col]
            product_id = sgc.product_id_by_sku(sku)
            print(f'{product_id}: {title}')
            sgc.update_product_title(product_id, title)

if __name__ == '__main__':
    main()