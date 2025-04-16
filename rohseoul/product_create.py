import logging
import re
import string
from google_api_interface import GoogleApiInterface
from shopify_graphql_client.client import ShopifyGraphqlClient

logging.basicConfig(level=logging.INFO)

def product_info_lists_from_sheet(gai:GoogleApiInterface, sheet_id, sheet_name, handle_suffix):
    start_row = 2
    column_product_attrs = dict(
        title=string.ascii_lowercase.index('e'),
        status=string.ascii_lowercase.index('a'),
        release_date=string.ascii_lowercase.index('c'),
        collection=string.ascii_lowercase.index('g'),
        category=string.ascii_lowercase.index('h'),
        description=string.ascii_lowercase.index('r'),
        size_text=string.ascii_lowercase.index('u'),
        material=string.ascii_lowercase.index('v'),
        made_in=string.ascii_lowercase.index('w'),
        )
    column_variant_attrs = {'カラー': string.ascii_lowercase.index('j')}
    column_variant_attrs.update(
        sku=string.ascii_lowercase.index('f'),
        price=string.ascii_lowercase.index('m'),
        stock=string.ascii_lowercase.index('n'),
        drive_link=string.ascii_lowercase.index('p'),
    )
    return gai.to_products_list(sheet_id, sheet_name, start_row, column_product_attrs,
                                column_variant_attrs,
                                handle_suffix=handle_suffix,
                                row_filter_func=lambda row: row[column_product_attrs['status']].strip() == 'NEW')

def get_size_table_html(size_text):
    lines = list(filter(None, map(str.strip, size_text.split('\n'))))
    kv_pairs = [line.rsplit(' ', 1) for line in lines]
    kv_pairs = [pair if len(pair) == 2 else ['Weight', pair[0]] for pair in kv_pairs]
    headers, values = zip(*kv_pairs)
    res = '<table><thead><tr>'
    for header in headers:
        res += f'<th>{header.replace(')', '')}</th>'
    res += '</tr></thead><tbody><tr>'
    for value in values:
        res += f'<td>{value}</td>'
    res += '</tr></tbody></table>'
    return res

def get_description_html(sgc:ShopifyGraphqlClient, description, material, size_text, made_in):
    product_care = '''革表面に跡や汚れなどが残る場合がありますが、天然皮革の特徴である不良ではございませんのでご了承ください。また、時間経過により金属の装飾や革の色が変化する場合がございますが、製品の欠陥ではありません。あらかじめご了承ください。
1: 熱や直射日光に長時間さらされると革に変色が生じることがありますのでご注意ください。
2: 変形の恐れがありますので、無理のない内容量でご使用ください。
3: 水に弱い素材です。濡れた場合は柔らかい布で水気を除去した後、乾燥させてください。
4: 使用しないときはダストバッグに入れ、涼しく風通しのいい場所で保管してください。
5: アルコール、オイル、香水、化粧品などにより製品が損傷することがありますので、ご使用の際はご注意ください。'''
    return sgc.get_description_html(description, product_care, material, size_text, made_in, get_size_table_html_func=get_size_table_html)

def create_a_product(sgc:ShopifyGraphqlClient, product_info, vendor, description_html_map):
    logging.info(f'creating {product_info["title"]}')
    description_html = description_html_map[product_info['title']]
    tags = ','.join([product_info['release_date'], product_info['collection'], product_info['category']])
    options = [[{'カラー': color}, price, sku] for color, price, sku
               in zip(product_info['color'], product_info['price'], product_info['sku'])]

    res = sgc.product_create(title=product_info['title'],
                             handle=product_info['handle'],
                             description_html=description_html,
                             vendor=vendor, tags=tags, option_lists=options)
    res2 = [sgc.enable_and_activate_inventory(sku, []) for sku in product_info['sku']]
    return (res, res2)

def create_products(sgc:ShopifyGraphqlClient, product_info_list, vendor):
    description_html_map = {product_info['title']: get_description_html(sgc,
                                                                        product_info['description'],
                                                                        product_info['material'],
                                                                        product_info['size_text'],
                                                                        product_info['made_in']) for product_info in product_info_list
                                                                        if product_info['description'] and product_info['size_text'] and product_info['made_in']}
    ress = []
    for product_info in product_info_list:
        ress.append(create_a_product(sgc, product_info, vendor, description_html_map))
    return ress

def update_stocks(sgc:ShopifyGraphqlClient, product_info_list):
    logging.info('updating inventory')
    location_id = sgc.location_id_by_name('Shop location')
    sku_stock_map = {sku: stock for product_info in product_info_list for sku, stock in zip(product_info['sku'], product_info['stock'])}
    return [sgc.set_inventory_quantity_by_sku_and_location_id(sku, location_id, stock)
            for sku, stock in sku_stock_map.items()]

def sort_key_func(k):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()
    return ['0'] if k.split('.')[0] == 'b1' else [convert(c) for c in re.split('([0-9]+)', k)]

def process_product_images(sgc:ShopifyGraphqlClient, gai:GoogleApiInterface, product_info, handle_suffix):
    product_id = sgc.product_id_by_handle('-'.join(product_info['title'].lower().split(' ') + [handle_suffix]))
    drive_ids = [gai.drive_link_to_id(drive_id) for drive_id in product_info['drive_link']]
    skuss = [[sku] for sku in product_info['sku']]

    local_paths = []
    variant_image_positions = []

    for drive_id, skus in zip(drive_ids, skuss):
        variant_image_positions.append(len(local_paths))
        local_paths += gai.drive_images_to_local(drive_id,
                                                 '/Users/taro/Downloads/rohseoul20250411/',
                                                 f'upload_20250411_{skus[0]}',
                                                 sort_key_func=sort_key_func)
    ress = []
    ress.append(sgc.upload_and_assign_images_to_product(product_id, local_paths))
    for skus, image_position in zip(skuss, variant_image_positions):
        ress.append(sgc.assign_image_to_skus_by_position(product_id, image_position, skus))
    return ress


def main():
    handle_suffix = '25ss-2nd'
    from utils import credentials
    import pprint
    cred = credentials('rohseoul')
    gai = GoogleApiInterface(cred.google_credential_path)
    product_info_list = product_info_lists_from_sheet(gai, cred.google_sheet_id, '25SS 2차오픈(4월)(Summer 25)', handle_suffix)
    len_list = len(product_info_list)
    product_info_list = [product_info for product_info in product_info_list if product_info['status'] == 'NEW']
    assert len_list == len(product_info_list)
    sgc = ShopifyGraphqlClient(cred.shop_name, cred.access_token)
    # ress = create_products(sgc, product_info_list, cred.shop_name)
    # pprint.pprint(ress)
    # ress = update_stocks(sgc, product_info_list)
    # pprint.pprint(ress)
    ress = []
    reprocess_from_title = 'Medium Mug shoulder bag Nylon'
    for index, product_info in enumerate(product_info_list):
        if product_info['title'] == reprocess_from_title:
            break
    for product_info in product_info_list[index:]:
        assert product_info['drive_link'], f"no drive link for {product_info['title']}"
        ress.append(process_product_images(sgc, gai, product_info, handle_suffix))
    pprint.pprint(ress)

if __name__ == '__main__':
    main()
