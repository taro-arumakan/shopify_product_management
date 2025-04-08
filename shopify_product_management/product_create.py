import string
from shopify_graphql_client.client import ShopifyGraphqlClient
from shopify_product_management.google_utils import gspread_access, get_sheet_index_by_title

def product_info_lists_from_sheet(gs_client, sheet_id, sheet_index=0):
    worksheet = gs_client.open_by_key(sheet_id).get_worksheet(sheet_index)
    rows = worksheet.get_all_values()

    start_row = 2           # 0 base
    title_column = string.ascii_lowercase.index('d')
    column_product_attrs = dict(
        release_date=string.ascii_lowercase.index('c'),
        collection=string.ascii_lowercase.index('f'),
        category=string.ascii_lowercase.index('h'),
        description=string.ascii_lowercase.index('q'),
        size_text=string.ascii_lowercase.index('t'),
        material=string.ascii_lowercase.index('u'),
        made_in=string.ascii_lowercase.index('v')
        )
    column_variant_attrs = dict(
        sku=string.ascii_lowercase.index('e'),
        color=string.ascii_lowercase.index('i'),
        price=string.ascii_lowercase.index('l'),
        drive_link=string.ascii_lowercase.index('o'),
        )
    current_title = ''
    res = []
    for row in rows[start_row:]:
        title = row[title_column]
        if title != current_title:
            if current_title:
                res.append(product_dict)            # done processing all variants of a product
            current_title, product_dict = title, {}
            product_dict['title'] = title
            for k, v in column_product_attrs.items():
                product_dict[k] = row[v]
        for k, v in column_variant_attrs.items():
            product_dict.setdefault(k, []).append(row[v])
    res.append(product_dict)                        # done processing the last product
    return res


def get_description_html(sgc, description, material, size_text, made_in):
    product_care = '''水や汗にさらされると、湿気によるカビや変色の恐れがあります。そのため、雨などに濡れないようご注意ください。

長時間水分に触れた場合は、革が水分を吸収する前にタオルで余分な水分を取り除いてください。内側に新聞紙などを詰め、風通しの良い場所で保管してください。'''
    return sgc.get_description_html(description, product_care, material, size_text, made_in)

def create_a_product(sgc, product_info, vendor):
    description_html = get_description_html(sgc, product_info['description'],
                                                 product_info['material'],
                                                 product_info['size_text'],
                                                 product_info['made_in'])
    options = [[{'カラー': color}, price, sku] for color, price, sku
               in zip(product_info['color'], product_info['price'], product_info['sku'])]
    tags = ','.join([product_info['release_date'], product_info['collection'], product_info['category']])
    return sgc.product_create(title=product_info['title'],
                              description_html=description_html,
                              vendor=vendor, tags=tags, option_lists=options)

def main():
    from dotenv import load_dotenv
    load_dotenv(override=True)
    import os
    access_token = os.getenv('ACCESS_TOKEN')
    shop_name = 'archive-epke'
    google_credential_path = os.getenv('GOOGLE_CREDENTIAL_PATH')
    gs_client = gspread_access(google_credential_path)
    sheet_id = '18YPrX-1CqvAxmrE1P6jrtmewkKZtiInngQw2bOTacWg'
    sheet_index = get_sheet_index_by_title(google_credential_path, sheet_id, '2025.4/10 Release')
    product_info_list = product_info_lists_from_sheet(gs_client, sheet_id, sheet_index)

    sgc = ShopifyGraphqlClient(shop_name, access_token)
    import pprint
    ress = []
    for product_info in product_info_list:
        pprint.pprint(product_info)
        res = create_a_product(sgc, product_info, 'archive-epke')
        ress.append(res)
    pprint.pprint(ress)


if __name__ == '__main__':
    main()