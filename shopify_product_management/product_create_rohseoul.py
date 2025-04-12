import datetime
import logging
import re
import string
from shopify_graphql_client.client import ShopifyGraphqlClient
from shopify_product_management.google_utils import get_rows, drive_link_to_id, drive_images_to_local

logging.getLogger().setLevel(logging.INFO)

def get_value(row, column_index, column_name):
    v = row[column_index]
    if column_name in ['release_date'] and isinstance(v, int):
        assert isinstance(v, int), f'expected int for {column_name}, got {type(v)}: {v}'
        v = str(datetime.date(1900, 1, 1) + datetime.timedelta(days=v))
    elif column_name in ['price', 'stock']:
        assert isinstance(v, int), f'expected int for {column_name}, got {type(v)}: {v}'
    else:
        assert isinstance(v, str), f'expected str for {column_name}, got {type(v)}: {v}'
        v = v.strip()
    return v

def product_info_lists_from_sheet(google_credential_path, sheet_id, sheet_name):
    rows = get_rows(google_credential_path, sheet_id=sheet_id, sheet_name=sheet_name)

    start_row = 16           # 0 base
    title_column = string.ascii_lowercase.index('e')
    column_product_attrs = dict(
        status=string.ascii_lowercase.index('a'),
        release_date=string.ascii_lowercase.index('c'),
        collection=string.ascii_lowercase.index('g'),
        category=string.ascii_lowercase.index('h'),
        description=string.ascii_lowercase.index('r'),
        size_text=string.ascii_lowercase.index('u'),
        material=string.ascii_lowercase.index('v'),
        made_in=string.ascii_lowercase.index('w'),
        sku=string.ascii_lowercase.index('f'),
        color=string.ascii_lowercase.index('j'),
        price=string.ascii_lowercase.index('m'),
        stock=string.ascii_lowercase.index('n'),
        drive_link=string.ascii_lowercase.index('p'),
        )
    res = []
    for row in rows[start_row:]:
        if row[column_product_attrs['status']].strip() != 'NEW':
            logging.info('skipping row %s', row[title_column])
            continue
        title = row[title_column]
        product_dict = dict(title=title)
        for k, ci in column_product_attrs.items():
            product_dict[k] = get_value(row, ci, k)
        product_dict['handle'] = '-'.join(title.lower().split(' ') + product_dict['color'].lower().split(' '))
        res.append(product_dict)                        # done processing the last product
    return res


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
    description_html = description_html_map[product_info['title']]
    tags = ','.join([product_info['release_date'], product_info['collection'], product_info['category']])
    res = sgc.product_create_default_variant(handle=product_info['handle'],
                                             title=product_info['title'],
                                             description_html=description_html,
                                             vendor=vendor, tags=tags,
                                             price=product_info['price'],
                                             sku=product_info['sku'])
    res2 = sgc.update_variation_value_metafield(res['id'], product_info['color'])
    res3 = sgc.enable_and_activate_inventory(product_info['sku'], [])
    return (res, res2, res3)

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
    location_id = sgc.location_id_by_name('Shop location')
    return [sgc.set_inventory_quantity_by_sku_and_location_id(product_info['sku'],
                                                              location_id,
                                                              product_info['stock'])
            for product_info in product_info_list]

def sort_key_func(k):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()
    return ['0'] if k.split('.')[0] == 'b1' else [convert(c) for c in re.split('([0-9]+)', k)]

def process_product_images(sgc:ShopifyGraphqlClient, product_info, google_credential_path):
    product_id = sgc.product_id_by_sku(product_info['sku'])
    drive_id = drive_link_to_id(product_info['drive_link'])
    local_paths = drive_images_to_local(google_credential_path, drive_id,
                                        '/Users/taro/Downloads/rohseoul20250411/',
                                        f'upload_20250411_{product_info['sku']}',
                                        sort_key_func=sort_key_func)
    return sgc.upload_and_assign_images_to_product(product_id, local_paths)

def main():
    from utils import credentials
    cred = credentials('rohseoul')
    product_info_list = product_info_lists_from_sheet(cred.google_credential_path, cred.google_sheet_id, '25SS 2차오픈(4월)(Summer 25)')
    sgc = ShopifyGraphqlClient(cred.shop_name, cred.access_token)
    import pprint
    ress = create_products(sgc, product_info_list, cred.shop_name)
    pprint.pprint(ress)
    ress = update_stocks(sgc, product_info_list)
    pprint.pprint(ress)
    ress = []
    for product_info in product_info_list:
        assert product_info['drive_link'], f"no drive link for {product_info['title']}"
        ress.append(process_product_images(sgc, product_info, cred.google_credential_path))
    pprint.pprint(ress)

if __name__ == '__main__':
    main()
