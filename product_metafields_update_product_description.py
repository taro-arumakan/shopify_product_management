import pprint
import utils
from product_metafields_update_size_table_html import text_to_html_tables_and_paragraphs

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


def update_product_description_metafield(client:utils.Client, title, desc, material, origin):
    product_description = get_product_description(desc, material, origin)
    product_id = client.product_id_by_title(title)
    return client.update_product_description_metafield(product_id, product_description)

def main():
    SHEET_TITLE = 'Products Master'
    client = utils.client('apricot-studios')
    rows = client.worksheet_rows(client.sheet_id, SHEET_TITLE)
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
            product_id = client.product_id_by_title(title)
            res1 = client.update_product_description_metafield(product_id, product_description)
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
