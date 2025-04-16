import string
import google_api_interface
import shopify_graphql_client
import utils

def main():
    cred = utils.credentials('rawrowr')
    sheet_name = '20250211_v3'
    gai = google_api_interface.get(cred.shop_name)
    rows = gai.get_rows(cred.google_sheet_id, sheet_name)
    title_col = string.ascii_lowercase.index('b')
    sku_col = string.ascii_lowercase.index('q')
    sgc = shopify_graphql_client.get(cred.shop_name)

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
