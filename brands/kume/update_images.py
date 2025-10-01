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


def process_product_images(client: utils.Client, product_info):
    product_id = client.product_id_by_title(product_info["title"])
    local_paths = []
    image_positions = []
    skuss = []
    for variant in product_info["options"]:
        assert variant[
            "drive_link"
        ], f"no drive link for {product_info['title'], {variant}}"
        drive_id = client.drive_link_to_id(variant["drive_link"])

        image_positions.append(len(local_paths))
        skuss.append([v2["sku"] for v2 in variant["options"]])
        local_paths += client.drive_images_to_local(
            drive_id,
            "/Users/taro/Downloads/kume20250417/",
            f"upload_20250417_{variant['options'][0]['sku']}",
        )
    ress = []
    ress.append(client.upload_and_assign_images_to_product(product_id, local_paths))
    for image_position, skus in zip(image_positions, skuss):
        ress.append(
            client.assign_image_to_skus_by_position(product_id, image_position, skus)
        )
    return ress


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
        ress.append(process_product_images(c, product_info))
    pprint.pprint(ress)


if __name__ == "__main__":
    main()
