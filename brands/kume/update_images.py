import logging
import re
import string
import utils

logging.basicConfig(level=logging.INFO)


def product_info_lists_from_sheet(gai: utils.Client, sheet_id, sheet_name):
    start_row = 2
    column_product_attrs = dict(
        title=string.ascii_lowercase.index("c"),
        # release_date=string.ascii_lowercase.index('b'),
        # collection=string.ascii_lowercase.index('e'),
        # category=string.ascii_lowercase.index('d'),
        # description=string.ascii_lowercase.index('g'),
        # size_text=string.ascii_lowercase.index('k'),
        # material=string.ascii_lowercase.index('j'),
        # made_in=string.ascii_lowercase.index('l'),
        # price=string.ascii_lowercase.index('o'),
    )
    option1_attrs = {"カラー": string.ascii_lowercase.index("p")}
    option1_attrs.update(
        drive_link=string.ascii_lowercase.index("q"),
    )
    option2_attrs = {"サイズ": string.ascii_lowercase.index("r")}
    option2_attrs.update(
        sku=string.ascii_lowercase.index("s"),
        stock=string.ascii_lowercase.index("t"),
    )
    return gai.to_products_list(
        sheet_id,
        sheet_name,
        start_row,
        column_product_attrs,
        option1_attrs,
        option2_attrs,
    )


def main():
    from utils import client
    import pprint

    c = client("kumej")
    titles = """Tweed Short Sleeve Blouse
Ribbon Boxer Shorts
Linen Pleated Long Skirt
H-line Knitted Skirt
Twisted Back Detail T-shirt""".split(
        "\n"
    )

    product_info_list = product_info_lists_from_sheet(c, c.sheet_id, "25ss")
    product_info_list = [
        product_info
        for product_info in product_info_list
        if product_info["title"] in titles
    ]
    assert len(titles) == len(product_info_list)
    ress = []
    for product_info in product_info_list:
        print(f'processing {product_info["title"]}')
        c.process_product_images(product_info)
    pprint.pprint(ress)


if __name__ == "__main__":
    main()
