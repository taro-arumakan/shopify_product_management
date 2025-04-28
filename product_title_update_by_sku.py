import string
import utils

def main():
    sheet_name = '20250211_v3'
    client = utils.client('rawrowr')
    rows = client.get_rows(client.google_sheet_id, sheet_name)
    title_col = string.ascii_lowercase.index('b')
    sku_col = string.ascii_lowercase.index('q')

    print(len(rows))
    for row in rows[2:]:
        title =row[title_col]
        if title:
            sku = row[sku_col]
            product_id = sgc.product_id_by_sku(sku)
            print(f'{product_id}: {title}')
            client.update_product_title(product_id, title)

if __name__ == '__main__':
    main()
