import re
import string
import utils

hidden_description_element_old = 'hidden_product_description_text'
fb_sync_description_element = 'fb_sync:product_description'

def get_updated_description(sgc:utils.Client, product_id):
    description_html = sgc.product_description_by_product_id(product_id)
    metafield_product_description = sgc.product_metafield_value_by_product_id(product_id, 'custom', 'product_description')
    metafield_product_description_converted = sgc.convert_rich_text_to_html(metafield_product_description)
    metafield_size_table_html = sgc.product_metafield_value_by_product_id(product_id, 'custom', 'size_table_html')
    description_html = re.sub(f'<{hidden_description_element_old}>.*</{hidden_description_element_old}>', '', description_html, flags=re.DOTALL)
    description_html = re.sub(f'<{fb_sync_description_element}>.*</{fb_sync_description_element}>', '', description_html, flags=re.DOTALL)
    updated_description = description_html
    updated_description += f'\n\n<{fb_sync_description_element}>'
    updated_description += f'\n{metafield_product_description_converted}'
    updated_description += f'\n<h5>サイズ</h5>\n{metafield_size_table_html}'
    updated_description += f'\n</{fb_sync_description_element}>'
    return updated_description

def main():
    shop_name = 'apricot-studios'
    client = utils.client(shop_name)
    rows = client.worksheet_rows(client.sheet_id, 'Products Master')
    for row in rows[1:]:
        title = row[string.ascii_lowercase.index('b')].strip()
        if title:
            product_id = client.product_id_by_title(title)
            print(product_id, title)
            updated_description = get_updated_description(client, product_id)

            print()
            print('updated:')
            print(updated_description)
            client.update_product_description(product_id, updated_description)


if __name__ == '__main__':
    main()
