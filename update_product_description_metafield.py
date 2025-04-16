import pprint
import google_api_interface
import shopify_graphql_client
from update_size_table_html_metafield import text_to_html_tables_and_paragraphs

def get_product_description(desc, material, origin):

  res = {
    'type': 'root',
    'children': [
                {'children': [{'type': 'text', 'value': desc.strip('\"')}], 'type': 'paragraph'},
                {'children': [{'type': 'text', 'value': ''}], 'type': 'paragraph'},
                {'children': [{'type': 'text', 'value': '素材'}], 'level': 5, 'type': 'heading'},
                {'children': [{'type': 'text', 'value': material.strip('\"')}], 'type': 'paragraph'},
                {'children': [{'type': 'text', 'value': '原産国'}], 'level': 5, 'type': 'heading'},
                {'children': [{'type': 'text', 'value': origin.strip('\"')}], 'type': 'paragraph'}
                ],
  }
  return res


def main():
    SHEET_TITLE = 'Products Master'
    gai = google_api_interface.get('apricot-studios')
    rows = gai.worksheet_rows(gai.sheet_id, SHEET_TITLE)
    sgc = shopify_graphql_client.get('apricot-studios')
    for row in rows[1:]:
        title = row[1].strip()
        if not title:
            continue

        print(f'processing {title}')
        desc = row[6]
        material = row[10]
        origin = row[13]

        product_description = get_product_description(desc, material, origin)
        if product_description:
            product_id = sgc.product_id_by_title(title)
            res1 = sgc.update_product_description_metafield(product_id, product_description)
            pprint.pprint(res1)
        else:
            print(f'product_description or size_table_html is empty for {title}')
            break

        # size_text = row[12]
        # size_table_html = text_to_html_tables_and_paragraphs(size_text)

        # if size_table_html:
        #     res2 = sgc.update_size_table_html_metafield(product_id, size_table_html)
        #     pprint.pprint(res2)


if __name__ == '__main__':
    main()
