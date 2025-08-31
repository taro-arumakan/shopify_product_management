import datetime
import logging
import string
import utils
from brands.liberaiders.update_descriptions import get_description
from brands.liberaiders.size_text_to_html_table import size_text_to_html_table


logging.basicConfig(level=logging.INFO)


def product_info_list_from_sheet(
    gai: utils.Client, sheet_id, sheet_name, row_filter_func=None
):
    start_row = 1
    column_product_attrs = dict(
        title=string.ascii_lowercase.index("b"),
        product_number=string.ascii_lowercase.index("c"),
        tags=string.ascii_lowercase.index("d"),
        price=string.ascii_lowercase.index("e"),
        description=string.ascii_lowercase.index("f"),
        product_care=string.ascii_lowercase.index("g"),
        material=string.ascii_lowercase.index("h"),
        weight=string.ascii_lowercase.index("i"),
        size_text_ja=string.ascii_lowercase.index("j"),
        size_text_en=string.ascii_lowercase.index("k"),
        made_in=string.ascii_lowercase.index("l"),
        drive_link=string.ascii_lowercase.index("m"),
    )
    option1_attrs = {"Color": string.ascii_lowercase.index("o")}
    option1_attrs.update(color_image_file_name=string.ascii_lowercase.index("n"))
    option2_attrs = {"Size": string.ascii_lowercase.index("p")}
    option2_attrs.update(
        sku=string.ascii_lowercase.index("q"),
        barcode=string.ascii_lowercase.index("r"),
        stock=string.ascii_lowercase.index("s"),
    )
    return gai.to_products_list(
        sheet_id,
        sheet_name,
        start_row,
        column_product_attrs,
        option1_attrs,
        option2_attrs,
        row_filter_func=row_filter_func,
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
        product_info["description"],
        product_info.get("material", ""),
        # product_info.get("made_in", ""),
    )
    tags = product_info["tags"]
    options = populate_option(product_info, "Color", "Size")
    res = sgc.product_create(
        title=product_info["title"],
        description_html=description_html,
        vendor=vendor,
        tags=tags,
        option_lists=options,
    )
    product_id = res["id"]
    update_metafields(sgc, product_id, product_info)

    res = [
        sgc.enable_and_activate_inventory(option2["sku"], [])
        for option1 in product_info["options"]
        for option2 in option1["options"]
    ]
    res += [
        sgc.update_inventory_item_weight_by_sku(option2["sku"], product_info["weight"])
        for option1 in product_info["options"]
        for option2 in option1["options"]
    ]
    res += [
        sgc.update_variant_barcode_by_sku(option2["sku"], option2["barcode"])
        for option1 in product_info["options"]
        for option2 in option1["options"]
    ]

    print(res)


def update_metafields(sgc: utils.Client, product_id, product_info):
    product_number = product_info["product_number"].strip()
    if product_number:
        res = sgc.update_product_number_metafield(product_id, product_number)
        print(res)
    size_text_ja = product_info.get("size_text_ja", "").strip()
    if size_text_ja:
        size_table_html_ja = size_text_to_html_table(size_text_ja)
        res = sgc.update_size_table_html_ja_metafield(product_id, size_table_html_ja)
        print(res)
    size_text_en = product_info.get("size_text_en", "").strip()
    if size_text_en:
        size_table_html_en = size_text_to_html_table(size_text_en)
        res = sgc.update_size_table_html_en_metafield(product_id, size_table_html_en)
        print(res)


def create_products(sgc: utils.Client, product_info_list, vendor):
    ress = []
    for product_info in product_info_list:
        ress.append(create_a_product(sgc, product_info, vendor))
    return ress


def update_stocks(sgc: utils.Client, product_info_list):
    logging.info("updating inventory")
    location_id = sgc.location_id_by_name("Liberaiders オンライン")
    sku_stock_map = {
        option2["sku"]: option2["stock"]
        for product_info in product_info_list
        for option1 in product_info["options"]
        for option2 in option1["options"]
        if option2.get("stock")
    }
    return [
        sgc.set_inventory_quantity_by_sku_and_location_id(sku, location_id, stock)
        for sku, stock in sku_stock_map.items()
    ]


def process_product_images(client: utils.Client, product_info):
    product_id = client.product_id_by_title(product_info["title"])
    local_paths = []
    if "drive_link" in product_info:
        drive_id = client.drive_link_to_id(product_info["drive_link"])
        local_paths += client.drive_images_to_local(
            drive_id,
            f"/Users/taro/Downloads/liberaiders{datetime.date.today():%Y%m%d}/",
            f"upload_{datetime.date.today():%Y%m%d}_{product_info['title'].replace('/', '_')}",
        )
        return client.upload_and_assign_images_to_product(product_id, local_paths)


def assign_variant_images(client: utils.Client, product_info_list):
    for product_info in product_info_list:
        product_id = client.product_by_title(product_info["title"])["id"]
        medias = client.medias_by_product_id(product_id)
        if not medias:
            logging.info(f"skipping processing of {product_info['title']}")
            continue
        for color_option in product_info["options"]:
            file_name = color_option.get("color_image_file_name")
            if not file_name:
                logging.info(
                    f"skipping processing of {color_option['Color']} of {product_info['title']}"
                )
                continue
            media = [m for m in medias if m["alt"].endswith(file_name)]
            if len(media) != 1:
                logging.warning(
                    f"check images of {product_info['title']} - {color_option['Color']}"
                )
                continue
            media = media[0]
            skus = [o2["sku"] for o2 in color_option["options"]]
            client.assign_image_to_skus(product_id, media["id"], skus)


def main():
    c = utils.client("liberaiders")
    product_info_list = product_info_list_from_sheet(
        c,
        c.sheet_id,
        "キャリー在庫",
    )

    # for index, product_info in enumerate(product_info_list):
    #     if product_info["title"] == "GARMENT DYED UTILITY PANTS":
    #         break
    # product_info_list = product_info_list[index:]
    # product_info_list = [pi for pi in product_info_list if pi['title'] == 'DESTINATION UNKNOWN L/S TEE']

    create_products(c, product_info_list, vendor="liberaiders")
    for product_info in product_info_list:
        process_product_images(c, product_info)
    assign_variant_images(c, product_info_list)
    update_stocks(c, product_info_list)


if __name__ == "__main__":
    main()
