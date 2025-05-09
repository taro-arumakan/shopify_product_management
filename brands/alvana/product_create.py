import logging
import string
import utils
from alvana.update_descriptions import get_description

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


def populate_option(product_info, option1_key, option2_key):
    return [
        [
            {option1_key: option1[option1_key], option2_key: option2[option2_key]},
            product_info["price"],
            option2["sku"],
        ]
        for option1 in product_info["options"]
        for option2 in option1["options"]
    ]


def create_a_product(sgc: utils.Client, product_info, vendor):
    logging.info(f'creating {product_info["title"]}')
    description_html = get_description(
        product_info["description"], product_info["material"], product_info["made_in"]
    )
    tags = product_info["tags"]
    options = populate_option(product_info, "カラー", "サイズ")
    res = sgc.product_create(
        title=product_info["title"],
        description_html=description_html,
        vendor=vendor,
        tags=tags,
        option_lists=options,
    )
    res2 = [
        sgc.enable_and_activate_inventory(option2["sku"], [])
        for option1 in product_info["options"]
        for option2 in option1["options"]
    ]
    return (res, res2)


def create_products(sgc: utils.Client, product_info_list, vendor):
    ress = []
    for product_info in product_info_list:
        ress.append(create_a_product(sgc, product_info, vendor))
    return ress


def update_stocks(sgc: utils.Client, product_info_list):
    logging.info("updating inventory")
    location_id = sgc.location_id_by_name("Shop location")
    sku_stock_map = {
        sku: stock
        for product_info in product_info_list
        for option1 in product_info["options"]
        for option2 in option1["options"]
        for sku, stock in zip(option2["sku"], option2["stock"])
        if option2["stock"]
    }
    return [
        sgc.set_inventory_quantity_by_sku_and_location_id(sku, location_id, stock)
        for sku, stock in sku_stock_map.items()
    ]


def process_product_images(client: utils.Client, product_info):
    product_id = client.product_id_by_title(product_info["title"])
    local_paths = []
    image_positions = []
    skuss = []
    for variant in product_info["options"]:
        assert variant[
            "drive_link"
        ], f"no drive link for {product_info['title'], {variant}}"
        if variant["drive_link"] == "no image":
            continue
        drive_id = client.drive_link_to_id(variant["drive_link"])
        image_positions.append(len(local_paths))
        skuss.append([v2["sku"] for v2 in variant["options"]])
        local_paths += client.drive_images_to_local(
            drive_id,
            "/Users/taro/Downloads/alvana20250418/",
            f"upload_202504187_{variant['options'][0]['sku']}",
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

    c = client("alvanas")
    product_info_list = product_info_list_from_sheet(c, c.sheet_id, "Product Master")
    for index, product_info in enumerate(product_info_list):
        if product_info["title"] == "FADE CENTER SEAM S/S TEE SHIRTS":
            break
    # ress = create_products(c, product_info_list[index:], vendor='alvana')
    # pprint.pprint(ress)
    ress = []
    for product_info in product_info_list[index:]:
        print(f'processing {product_info["title"]}')
        ress.append(process_product_images(c, product_info))
    pprint.pprint(ress)


if __name__ == "__main__":
    main()
