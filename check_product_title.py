import google_api_interface
import shopify_graphql_client


def main():
    shop_name = 'archive-epke'
    sheet_name = '2025.4/10 Release'

    gai = google_api_interface.get(shop_name)
    sgc = shopify_graphql_client.get(shop_name)
    rows = gai.worksheet_rows(gai.sheet_id, sheet_name)

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
