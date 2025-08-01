import datetime
import logging
import string
import utils
from brands.gbh.get_size_table_html import (
    size_table_html_from_size_dict,
    size_table_html,
)

tags_map = {"COSME": "COSMETIC"}

logging.basicConfig(level=logging.INFO)
column_indices = dict(
    release_date=string.ascii_lowercase.index("b"),
    category=string.ascii_lowercase.index("d"),
    category2=string.ascii_lowercase.index("e"),
    title=string.ascii_lowercase.index("f"),
    sku=string.ascii_lowercase.index("i"),
    price=string.ascii_lowercase.index("l"),
    stock=string.ascii_lowercase.index("m"),
    drive_link=string.ascii_lowercase.index("o"),
    description=string.ascii_lowercase.index("q"),
    product_care=string.ascii_lowercase.index("s"),
    size_text=string.ascii_lowercase.index("u"),
    material=string.ascii_lowercase.index("v"),
    made_in=string.ascii_lowercase.index("w"),
)
column_indices["カラー"] = string.ascii_lowercase.index("g")
column_indices["Scent"] = string.ascii_lowercase.index("g")
column_indices["サイズ"] = string.ascii_lowercase.index("h")


def product_info_list_from_sheet_no_options(
    gai: utils.Client, sheet_id, sheet_name, row_filter_func=None
):
    start_row = 2
    column_product_attrs = [
        "title",
        "category",
        "category2",
        "release_date",
        "description",
        "product_care",
        "material",
        "made_in",
        "drive_link",
        "size_text",
        "price",
        "sku",
        "stock",
    ]
    column_product_attrs = {attr: column_indices[attr] for attr in column_product_attrs}
    return gai.to_products_list(
        sheet_id,
        sheet_name,
        start_row,
        column_product_attrs,
        row_filter_func=row_filter_func,
    )


def product_info_list_from_sheet_scent_and_size_options(
    gai: utils.Client, sheet_id, sheet_name, titles
):
    start_row = 2
    column_product_attrs = [
        "title",
        "category",
        "category2",
        "release_date",
        "description",
        "product_care",
        "material",
        "made_in",
        "drive_link",
        "size_text",
    ]
    option1_attrs = ["Scent"]
    option2_attrs = ["サイズ", "price", "sku", "stock"]
    return gai.to_products_list(
        sheet_id,
        sheet_name,
        start_row,
        {attr: column_indices[attr] for attr in column_product_attrs},
        {attr: column_indices[attr] for attr in option1_attrs},
        {attr: column_indices[attr] for attr in option2_attrs},
        row_filter_func=lambda row: row[string.ascii_lowercase.index("f")] in titles,
    )


def product_info_list_from_sheet_size_options(
    gai: utils.Client, sheet_id, sheet_name, titles
):
    start_row = 2
    column_product_attrs = [
        "title",
        "category",
        "category2",
        "release_date",
        "description",
        "product_care",
        "material",
        "made_in",
    ]
    option1_attrs = ["サイズ", "drive_link", "price", "sku", "stock", "size_text"]
    return gai.to_products_list(
        sheet_id,
        sheet_name,
        start_row,
        {attr: column_indices[attr] for attr in column_product_attrs},
        {attr: column_indices[attr] for attr in option1_attrs},
        row_filter_func=lambda row: row[string.ascii_lowercase.index("f")] in titles,
    )


def product_info_list_from_sheet_color_options(
    gai: utils.Client, sheet_id, sheet_name, titles
):
    start_row = 1
    column_product_attrs = [
        "title",
        "category",
        "category2",
        "release_date",
        "description",
        "product_care",
        "material",
        "made_in",
        "size_text",
    ]
    option1_attrs = ["カラー", "drive_link", "price", "sku", "stock"]
    return gai.to_products_list(
        sheet_id,
        sheet_name,
        start_row,
        {attr: column_indices[attr] for attr in column_product_attrs},
        {attr: column_indices[attr] for attr in option1_attrs},
        row_filter_func=lambda row: row[string.ascii_lowercase.index("f")] in titles,
    )


def create_a_product(
    sgc: utils.Client,
    product_info,
    vendor,
    size_texts=None,
    get_size_table_html_func=None,
):
    logging.info(f'creating {product_info["title"]}')
    description_html = sgc.get_description_html(
        description=product_info["description"],
        product_care=product_info["product_care"],
        material=product_info["material"],
        size_text=size_texts or product_info["size_text"],
        made_in=product_info["made_in"],
        get_size_table_html_func=get_size_table_html_func,
    )
    tags = ",".join(
        [
            tags_map.get(product_info["category"], product_info["category"]),
            tags_map.get(product_info["category2"], product_info["category2"]),
            product_info["release_date"],
            "New Arrival",
        ]
    )
    return sgc.create_a_product(
        product_info=product_info,
        vendor=vendor,
        description_html=description_html,
        tags=tags,
        location_names=["Shop location"],
    )


def create_products(
    sgc: utils.Client, product_info_list, vendor, get_size_table_html_func=None
):
    ress = []
    for product_info in product_info_list:
        ress.append(
            create_a_product(
                sgc,
                product_info,
                vendor,
                get_size_table_html_func=get_size_table_html_func,
            )
        )
    ress2 = update_stocks(sgc, product_info_list, ["Shop location"])
    return ress, ress2


def update_stocks(sgc: utils.Client, product_info_list, location_name):
    logging.info("updating inventory")
    location_id = sgc.location_id_by_name(location_name)
    sku_stock_map = {}
    [
        sku_stock_map.update(sgc.get_sku_stocks_map(product_info))
        for product_info in product_info_list
    ]
    return [
        sgc.set_inventory_quantity_by_sku_and_location_id(sku, location_id, stock)
        for sku, stock in sku_stock_map.items()
    ]


def main():
    import pprint

    client = utils.client("gbhjapan")
    vendor = "GBH"
    # titles_with_size_options = ['DRINKING GLASS / THIN']
    # product_info_list = product_info_list_from_sheet_size_options(client, client.sheet_id, 'HOME&COSMETIC_25.04.24', titles_with_size_options)
    # size_texts = {option1['サイズ']: option1['size_text'] for option1 in product_info['options']}
    # ress = create_products(client, product_info_list, vendor, size_texts, size_table_html_from_size_dict)
    # for res in ress:
    #     logging.info(res)

    product_info_list = product_info_list_from_sheet_no_options(
        client,
        client.sheet_id,
        "GIFT SET 25.06.18 SET",
        row_filter_func=lambda row: row[column_indices["title"]]
        in [
            "DAILY HAIR CARE GIFT SET",
            "DAILY FRAGRANCE GIFT SET",
            "DAILY FRAGRANCE PREMIUM GIFT SET",
        ],
    )
    # ress = create_products(
    #     client, product_info_list, vendor, get_size_table_html_func=lambda x: x
    # )
    # pprint.pprint(ress)
    # ress = []
    # for product_info in product_info_list:
    #     ress.append(
    #         client.process_product_images(
    #             product_info, "/Users/taro/Downloads/gbh20250615/", "upload_20250615_"
    #         )
    #     )
    # pprint.pprint(ress)
    res = update_stocks(client, product_info_list, "Shop location")
    pprint.pprint(res)


if __name__ == "__main__":
    main()
