import pprint
import string
import google_api_interface
import shopify_graphql_client

def get_product_description(desc, material, size_text, origin):

  res = {
    'type': 'root',
    'children': [
                {'children': [{'type': 'text', 'value': desc.strip('\"')}], 'type': 'paragraph'},
                {'children': [{'type': 'text', 'value': ''}], 'type': 'paragraph'},
                {'children': [{'type': 'text', 'value': '素材'}], 'level': 5, 'type': 'heading'},
                {'children': [{'type': 'text', 'value': material.strip('\"')}], 'type': 'paragraph'},
                {'children': [{'type': 'text', 'value': 'サイズ'}], 'level': 5, 'type': 'heading'},
                {'children': [{'type': 'text', 'value': size_text.strip('\"').strip()}], 'type': 'paragraph'},
                {'children': [{'type': 'text', 'value': '原産国'}], 'level': 5, 'type': 'heading'},
                {'children': [{'type': 'text', 'value': origin.strip('\"')}], 'type': 'paragraph'}
                ],
  }
  return res


def main():
    shop_name = 'rawrowr'
    gai = google_api_interface.get(shop_name)
    rows = gai.worksheet_rows(gai.sheet_id, '20250211_v3')
    sgc = shopify_graphql_client.get(shop_name)
    for row in rows[2:]:
        title = row[1].strip()
        if not title:
            continue

        print(f'processing {title}')
        desc = row[string.ascii_lowercase.index('g')]
        material = row[string.ascii_lowercase.index('j')]
        size_text = row[string.ascii_lowercase.index('k')]
        origin = row[string.ascii_lowercase.index('l')]

        product_description = get_product_description(desc, material, size_text, origin)
        assert product_description, f'product_description is empty  for {title}'
        product_id = sgc.product_id_by_title(title)
        res1 = sgc.update_product_description_metafield(product_id, product_description)
        pprint.pprint(res1)


if __name__ == '__main__':
    main()
