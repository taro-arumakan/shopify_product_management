import logging
import string
import utils
from gbh.get_size_table_html import size_table_html_from_size_dict_space_pairs

logging.basicConfig(level=logging.INFO)

def product_info_list_from_sheet_color_and_size(gai:utils.Client, sheet_id, sheet_name):
    start_row = 2
    column_product_attrs = dict(
        title=string.ascii_lowercase.index('f'),
        collection=string.ascii_lowercase.index('c'),
        category=string.ascii_lowercase.index('d'),
        category2=string.ascii_lowercase.index('e'),
        release_date=string.ascii_lowercase.index('b'),
        description=string.ascii_lowercase.index('q'),
        product_care=string.ascii_lowercase.index('s'),
        material=string.ascii_lowercase.index('v'),
        made_in=string.ascii_lowercase.index('w'),

        )
    option1_attrs = {'カラー': string.ascii_lowercase.index('g')}
    option1_attrs.update(
        drive_link=string.ascii_lowercase.index('o'),
    )
    option2_attrs = {'サイズ': string.ascii_lowercase.index('h')}
    option2_attrs.update(
        price=string.ascii_lowercase.index('l'),
        sku=string.ascii_lowercase.index('i'),
        stock=string.ascii_lowercase.index('m'),
        size_text=string.ascii_lowercase.index('u'),
    )
    return gai.to_products_list(sheet_id, sheet_name, start_row, column_product_attrs,
                                option1_attrs, option2_attrs)

def create_a_product(sgc:utils.Client, product_info, vendor, size_texts=None, get_size_table_html_func=None, additional_tags=None):
    logging.info(f'creating {product_info["title"]}')
    description_html = sgc.get_description_html(description=product_info['description'],
                                                product_care=product_info['product_care'],
                                                material=product_info['material'],
                                                size_text=size_texts or product_info['size_text'],
                                                made_in=product_info['made_in'],
                                                get_size_table_html_func=get_size_table_html_func)
    tags = ','.join([product_info['category'], product_info['category2'], product_info['release_date']] + additional_tags or [])
    return sgc.create_a_product(product_info=product_info, vendor=vendor, description_html=description_html, tags=tags, location_names=['Shop location'])

def create_products(sgc:utils.Client, product_info_list, vendor, get_size_table_html_func=None, additional_tags=None):
    ress = []
    for product_info in product_info_list:
        size_texts = {option2['サイズ']: option2['size_text'] for option1 in product_info['options'] for option2 in option1['options']}
        ress.append(create_a_product(sgc, product_info, vendor, size_texts=size_texts, get_size_table_html_func=get_size_table_html_func, additional_tags=additional_tags))
    ress2 = update_stocks(sgc, product_info_list, ['Shop location'])
    return ress, ress2

def update_stocks(sgc:utils.Client, product_info_list, location_name):
    logging.info('updating inventory')
    location_id = sgc.location_id_by_name(location_name)
    sku_stock_map = {}
    for product_info in product_info_list:
        sku_stock_map.update(sgc.get_sku_stocks_map(product_info))
    ress = []
    for sku, stock in sku_stock_map.items():
        ress.append(sgc.set_inventory_quantity_by_sku_and_location_id(sku, location_id, stock))
    return ress

def main():
    import pprint
    client = utils.client('gbhjapan')
    vendor = 'GBH'
    product_info_list = product_info_list_from_sheet_color_and_size(client, client.sheet_id, 'APPAREL SS 25.04.28')
    ress = create_products(client, product_info_list, vendor, size_table_html_from_size_dict_space_pairs, additional_tags=['New Arrival', '25SS (Summer)'])
    pprint.pprint(ress)
    ress = []
    for product_info in product_info_list:
        ress.append(client.process_product_images(product_info, '/Users/taro/Downloads/gbh20250425/', 'upload_20250425_'))
    pprint.pprint(ress)

if  __name__ == '__main__':
    main()
