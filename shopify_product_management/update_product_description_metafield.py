import os
from dotenv import load_dotenv
from shopify_product_management import shopify_utils
from shopify_product_management.google_utils import gspread_access, get_sheet_index_by_title
from shopify_product_management.update_size_table_html_metafield import text_to_html_tables_and_paragraphs

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
    load_dotenv(override=True)
    SHOPNAME = 'apricot-studios'
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    print(ACCESS_TOKEN)
    GOOGLE_CREDENTIAL_PATH = os.getenv('GOOGLE_CREDENTIAL_PATH')

    GSPREAD_ID = '1yVzpgcrgNR7WxUYfotEnhYFMbc79l1O4rl9CamB2Kqo'
    SHEET_TITLE = 'Products Master'

    sheet_index = get_sheet_index_by_title(GOOGLE_CREDENTIAL_PATH, GSPREAD_ID, SHEET_TITLE)
    worksheet = gspread_access(GOOGLE_CREDENTIAL_PATH).open_by_key(GSPREAD_ID).get_worksheet(sheet_index)
    rows = worksheet.get_all_values()

    for row in rows[1:]:
      title = row[1].strip()
      if not title:
         continue

      print(f'processing {title}')
      desc = row[6]
      material = row[10]
      origin = row[13]

      product_description = get_product_description(desc, material, origin)
      size_text = row[12]
      size_table_html = text_to_html_tables_and_paragraphs(size_text)

      if product_description and size_table_html:
          product_id = shopify_utils.product_id_by_title(SHOPNAME, ACCESS_TOKEN, title)
          res = shopify_utils.update_product_description_and_size_table_html_metafields(SHOPNAME, ACCESS_TOKEN, product_id, product_description, size_table_html)
          # import pprint
          # pprint.pprint(res)
          # print(size_table_html)
      else:
          print(f'product_description or size_table_html is empty for {title}')
          break


if __name__ == '__main__':
    main()
