import string
import utils

def main():
    sheet_id = '1MYGLW9pekrhra8bXqIA2H2t3g3kETUWIDcFnjdW4j84'
    price_column = string.ascii_uppercase.index('N')
    title_column = string.ascii_uppercase.index('A')
    client = utils.client('archive-epke')
    rows = client.worksheet_rows(sheet_id, '現 JP EC 価格改定 ')
    for row in rows[4:]:
        title = row[title_column]
        price = int(row[price_column])
        products = client.products_by_title(title, additional_fields=['status'])

        for product in products:
            for variant in product['variants']['nodes']:
                variant_price = int(variant['price'])
                if price and variant_price != price:
                    print(f"Status: {product['status']}, Title: {title}, Variant ID: {variant['id']}, Price: {variant_price}, Expected: {price}")
                elif not price:
                    print(f"Status: {product['status']}, Title: {title}, Variant ID: {variant['id']}, Price: {variant_price}, Expected: {price}")


if __name__ == '__main__':
    main()
