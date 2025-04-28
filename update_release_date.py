import datetime
import string
import utils
import pprint

tag_to_replace = '2025-04-28'

def main():
    client = utils.client('gbhjapan')
    rows = client.worksheet_rows(client.sheet_id, sheet_title='APPAREL SS 25.04.28コピー')
    for row in rows[3:]:
        title = row[string.ascii_lowercase.index('f')]
        if title:
            release_date = str(datetime.date(1899, 12, 30) + datetime.timedelta(days=row[string.ascii_lowercase.index('b')]))
            product = client.product_by_title(title.strip())
            tags = product['tags']
            new_tags = [release_date if t == tag_to_replace else t for t in tags]
            if tags != new_tags:
                client.update_product_tags(product['id'], new_tags)

if __name__ == '__main__':
    main()
