import datetime
import logging
import string
import utils
from gbh.get_size_table_html import size_table_html_from_size_dict, size_table_html

logging.basicConfig(level=logging.INFO)

def product_info_list_from_sheet_no_options(gai:utils.Client, sheet_id, sheet_name, raw_filter_func):
    start_row = 2
    column_product_attrs = dict(
        title=string.ascii_lowercase.index('f'),
        category=string.ascii_lowercase.index('d'),
        category2=string.ascii_lowercase.index('e'),
        release_date=string.ascii_lowercase.index('b'),
        description=string.ascii_lowercase.index('q'),
        product_care=string.ascii_lowercase.index('s'),
        material=string.ascii_lowercase.index('v'),
        made_in=string.ascii_lowercase.index('w'),
        drive_link=string.ascii_lowercase.index('o'),
        size_text=string.ascii_lowercase.index('u'),
        price=string.ascii_lowercase.index('l'),
        sku=string.ascii_lowercase.index('i'),
        stock=string.ascii_lowercase.index('m'),
    )
    return gai.to_products_list(sheet_id, sheet_name, start_row, column_product_attrs, row_filter_func=raw_filter_func)

def product_info_list_from_sheet_scent_and_size_options(gai:utils.Client, sheet_id, sheet_name, titles_with_scent_and_size_options):
    start_row = 2
    column_product_attrs = dict(
        title=string.ascii_lowercase.index('f'),
        category=string.ascii_lowercase.index('d'),
        category2=string.ascii_lowercase.index('e'),
        release_date=string.ascii_lowercase.index('b'),
        description=string.ascii_lowercase.index('q'),
        product_care=string.ascii_lowercase.index('s'),
        material=string.ascii_lowercase.index('v'),
        made_in=string.ascii_lowercase.index('w'),
        drive_link=string.ascii_lowercase.index('o'),
        size_text=string.ascii_lowercase.index('u'),
        )
    option1_attrs = {'Scent': string.ascii_lowercase.index('g')}
    option2_attrs = {'サイズ': string.ascii_lowercase.index('h')}
    option2_attrs.update(
        price=string.ascii_lowercase.index('l'),
        sku=string.ascii_lowercase.index('i'),
        stock=string.ascii_lowercase.index('m'),
    )
    return gai.to_products_list(sheet_id, sheet_name, start_row, column_product_attrs,
                                option1_attrs, option2_attrs, row_filter_func=lambda row: row[string.ascii_lowercase.index('f')] in titles_with_scent_and_size_options)

def product_info_list_from_sheet_size_options(gai:utils.Client, sheet_id, sheet_name, titles_with_size_options):
    start_row = 2
    column_product_attrs = dict(
        title=string.ascii_lowercase.index('f'),
        category=string.ascii_lowercase.index('d'),
        category2=string.ascii_lowercase.index('e'),
        release_date=string.ascii_lowercase.index('b'),
        description=string.ascii_lowercase.index('q'),
        product_care=string.ascii_lowercase.index('s'),
        material=string.ascii_lowercase.index('v'),
        made_in=string.ascii_lowercase.index('w'),
        )
    option1_attrs = {'サイズ': string.ascii_lowercase.index('h')}
    option1_attrs.update(
        drive_link=string.ascii_lowercase.index('o'),
        price=string.ascii_lowercase.index('l'),
        sku=string.ascii_lowercase.index('i'),
        stock=string.ascii_lowercase.index('m'),
        size_text=string.ascii_lowercase.index('u'),
    )
    return gai.to_products_list(sheet_id, sheet_name, start_row, column_product_attrs,
                                option1_attrs, row_filter_func=lambda row: row[string.ascii_lowercase.index('f')] in titles_with_size_options)

def create_a_product(sgc:utils.Client, product_info, vendor, size_texts=None, get_size_table_html_func=None):
    logging.info(f'creating {product_info["title"]}')
    description_html = sgc.get_description_html(description=product_info['description'],
                                                product_care=product_info['product_care'],
                                                material=product_info['material'],
                                                size_text=size_texts or product_info['size_text'],
                                                made_in=product_info['made_in'],
                                                get_size_table_html_func=get_size_table_html_func)
    tags = ','.join([product_info['category'], product_info['category2'], product_info['release_date']])
    return sgc.create_a_product(product_info=product_info, vendor=vendor, description_html=description_html, tags=tags, location_names=['Shop location'])

def create_products(sgc:utils.Client, product_info_list, vendor, get_size_table_html_func=None):
    ress = []
    for product_info in product_info_list:
        ress.append(create_a_product(sgc, product_info, vendor, get_size_table_html_func=get_size_table_html_func))
    ress2 = update_stocks(sgc, product_info_list, ['Shop location'])
    return ress, ress2

def update_stocks(sgc:utils.Client, product_info_list, location_name):
    logging.info('updating inventory')
    location_id = sgc.location_id_by_name(location_name)
    sku_stock_map = {}
    [sku_stock_map.update(sgc.get_sku_stocks_map(product_info)) for product_info in product_info_list]
    return [sgc.set_inventory_quantity_by_sku_and_location_id(sku, location_id, stock)
            for sku, stock in sku_stock_map.items()]


def main():
    import pprint
    client = utils.client('gbhjapan')
    vendor = 'GBH'
    titles_with_size_options = ['DRINKING GLASS / THIN']
    # product_info_list = product_info_list_from_sheet_size_options(client, client.sheet_id, 'HOME&COSMETIC_25.04.24', titles_with_size_options)
    # size_texts = {option1['サイズ']: option1['size_text'] for option1 in product_info['options']}
    # ress = create_products(client, product_info_list, vendor, size_texts, size_table_html_from_size_dict)
    # for res in ress:
    #     logging.info(res)

    titles_with_scent_and_size_options = ['FRAGRANCE SANITIZER SPRAY']
    # product_info_list = product_info_list_from_sheet_scent_and_size_options(client, client.sheet_id, 'HOME&COSMETIC_25.04.24', titles_with_scent_and_size_options)
    # ress = create_products(client, product_info_list, vendor, get_size_table_html_func=lambda x: x)

    def filter_func(row):
        return (isinstance(row[string.ascii_lowercase.index('b')], int) and
                datetime.date(1899, 12, 30) + datetime.timedelta(days=row[string.ascii_lowercase.index('b')]) == datetime.date(2025, 4, 24) and
                row[string.ascii_lowercase.index('f')] not in titles_with_size_options + titles_with_scent_and_size_options)
    product_info_list = product_info_list_from_sheet_no_options(client, client.sheet_id, 'HOME&COSMETIC_25.04.24', raw_filter_func=filter_func)
    ress = create_products(client, product_info_list, vendor, get_size_table_html_func=size_table_html)
    pprint.pprint(ress)
    ress = []
    for product_info in product_info_list:
        ress.append(client.process_product_images(product_info, '/Users/taro/Downloads/gbh20250421/', 'upload_20250421_'))
    pprint.pprint(ress)

if  __name__ == '__main__':
    main()
