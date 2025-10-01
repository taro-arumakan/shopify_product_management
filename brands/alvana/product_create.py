import datetime
import logging
import string
import utils
from brands.alvana.update_descriptions import get_description

logging.basicConfig(level=logging.INFO)


def product_info_list_from_sheet(gai: utils.Client, sheet_id, sheet_name):
    start_row = 1
    column_product_attrs = dict(
        title=string.ascii_lowercase.index("b"),
        tags=string.ascii_lowercase.index("c"),
        price=string.ascii_lowercase.index("d"),
        description=string.ascii_lowercase.index("e"),
        product_care=string.ascii_lowercase.index("f"),
        material=string.ascii_lowercase.index("g"),
        size_text=string.ascii_lowercase.index("h"),
        made_in=string.ascii_lowercase.index("i"),
    )
    option1_attrs = {"カラー": string.ascii_lowercase.index("j")}
    option1_attrs.update(
        drive_link=string.ascii_lowercase.index("k"),
    )
    option2_attrs = {"サイズ": string.ascii_lowercase.index("l")}
    option2_attrs.update(
        sku=string.ascii_lowercase.index("m"),
        stock=string.ascii_lowercase.index("n"),
    )
    return gai.to_products_list(
        sheet_id,
        sheet_name,
        start_row,
        column_product_attrs,
        option1_attrs,
        option2_attrs,
    )


def create_a_product(sgc: utils.Client, product_info, vendor, locations):
    logging.info(f'creating {product_info["title"]}')
    description_html = get_description(
        product_info["description"], product_info["material"], product_info["made_in"]
    )
    tags = product_info["tags"]
    res = sgc.create_a_product(product_info, vendor, description_html, tags, locations)
    return res


def main():
    from utils import client
    import pprint

    c = client("alvanas")
    location = "Jingumae"
    product_info_list = product_info_list_from_sheet(c, c.sheet_id, "Product Master")
    for index, product_info in enumerate(product_info_list):
        if product_info["title"] == "HANDSPUN HEMP OPEN COLLAR SHIRTS":
            break
    product_info_list = product_info_list[index:]
    for product_info in product_info_list:
        res = create_a_product(c, product_info, "alvana", [location])
        pprint.pprint(res)
    for product_info in product_info_list:
        res = c.process_product_images(
            product_info,
            local_dir=f"/Users/taro/Downloads/alvana{datetime.date.today():%Y%m%d}/",
            filename_prefix=f"upload_{datetime.date.today():%Y%m%d}",
        )
        pprint.pprint(res)
    c.update_stocks(product_info_list, location)


if __name__ == "__main__":
    main()
