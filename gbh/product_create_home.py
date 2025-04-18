import logging
import string
import utils
from gbh.get_size_table_html import size_table_html_from_size_dict

logging.basicConfig(level=logging.INFO)

def product_info_list_from_sheet_size_options(gai:utils.Client, sheet_id, sheet_name, titles_with_size_options):
    start_row = 1
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

def enable_and_activate_inventory(sgc:utils.Client, product_info, options=None):
    options = options or sgc.populate_option(product_info)
    res2 = [sgc.enable_and_activate_inventory(option[2], []) for option in options]
    return res2

def create_a_product(sgc:utils.Client, product_info, vendor):
    logging.info(f'creating {product_info["title"]}')
    size_texts = {option1['サイズ']: option1['size_text'] for option1 in product_info['options']}
    description_html = sgc.get_description_html(description=product_info['description'],
                                                product_care=product_info['product_care'],
                                                material=product_info['material'],
                                                size_text=size_texts,
                                                made_in=product_info['made_in'],
                                                get_size_table_html_func=size_table_html_from_size_dict)
    tags = ','.join([product_info['category'], product_info['category2'], product_info['release_date']])
    options = sgc.populate_option(product_info)
    res = sgc.product_create(title=product_info['title'],
                             description_html=description_html,
                             vendor=vendor, tags=tags, option_lists=options)
    res2 = enable_and_activate_inventory(sgc, product_info, options)
    return (res, res2)

def create_products(sgc:utils.Client, product_info_list, vendor):
    ress = []
    for product_info in product_info_list:
        ress.append(create_a_product(sgc, product_info, vendor))
    return ress

def update_stocks(sgc:utils.Client, product_info_list, location_name):
    logging.info('updating inventory')
    location_id = sgc.location_id_by_name(location_name)
    sku_stock_map = {}
    [sku_stock_map.update(sgc.get_sku_stocks_map(product_info)) for product_info in product_info_list]
    return [sgc.set_inventory_quantity_by_sku_and_location_id(sku, location_id, stock)
            for sku, stock in sku_stock_map.items()]

def process_product_images(client:utils.Client, product_info):
    product_id = client.product_id_by_title(product_info['title'])
    local_paths = []
    image_positions = []
    drive_links, skuss = client.populate_drive_ids_and_skuss(product_info)
    for drive_id, skus in zip(drive_links, skuss):
        image_positions.append(len(local_paths))
        local_paths += client.drive_images_to_local(drive_id,
                                                    '/Users/taro/Downloads/gbh20250418/',
                                                    f'upload_202504187_{skus[0]}')
    ress = []
    ress.append(client.upload_and_assign_images_to_product(product_id, local_paths))
    for image_position, skus in zip(image_positions, skuss):
        ress.append(client.assign_image_to_skus_by_position(product_id, image_position, skus))
    return ress

def main():
    client = utils.client('gbhjapan')
    titles_with_size_options = ['DRINKING GLASS / THIN']
    product_info_list = product_info_list_from_sheet_size_options(client, client.sheet_id, 'HOME&COSMETIC_25.04.24', titles_with_size_options)
    # vendor = 'GBH'
    # ress = create_products(client, product_info_list, vendor)

    # ress = [enable_and_activate_inventory(client, product_info) for product_info in product_info_list]
    # for res in ress:
    #     logging.info(res)
    ress = []
    for product_info in product_info_list:
        ress.append(client.process_product_images(product_info, '/Users/taro/Downloads/gbh20250418/', 'upload_202504187_'))
    import pprint
    pprint.pprint(ress)

if  __name__ == '__main__':
    main()
