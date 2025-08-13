import datetime
import logging
import string
import utils
from brands.alvana.update_descriptions import get_description


logging.basicConfig(level=logging.INFO)


def product_info_list_from_sheet(
    gai: utils.Client, sheet_id, sheet_name, row_filter_func=None
):
    start_row = 946
    column_product_attrs = dict(
        title=string.ascii_lowercase.index("b"),
        tags=string.ascii_lowercase.index("c"),
        price=string.ascii_lowercase.index("e"),
        description=string.ascii_lowercase.index("g"),
        product_care_option=string.ascii_lowercase.index("h"),
        material=string.ascii_lowercase.index("j"),
        size_text=string.ascii_lowercase.index("k"),
        made_in=string.ascii_lowercase.index("l"),
    )
    option1_attrs = {"Color": string.ascii_lowercase.index("m")}
    option1_attrs.update(
        drive_link=string.ascii_lowercase.index("n"),
        sku=string.ascii_lowercase.index("o"),
        stock=string.ascii_lowercase.index("p"),
    )
    return gai.to_products_list(
        sheet_id,
        sheet_name,
        start_row,
        column_product_attrs,
        option1_attrs,
        row_filter_func=row_filter_func,
    )


def populate_option(product_info, option1_key):
    return [
        [
            {option1_key: option1[option1_key]},
            product_info["price"],
            option1["sku"],
        ]
        for option1 in product_info["options"]
    ]


def create_a_product(sgc: utils.Client, product_info, vendor):
    logging.info(f'creating {product_info["title"]}')
    try:
        exists = sgc.product_by_title(product_info["title"])
        logging.info(f'skipping creation of {product_info["title"]} - {exists["id"]}')
        product_id = exists["id"]
    except utils.NoProductsFoundException as ex:
        logging.info(ex)
        description_html = get_description(
            product_info["description"],
            product_info.get("material", ""),
            product_info.get("made_in", ""),
        )
        tags = product_info["tags"]
        options = populate_option(product_info, "Color")
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
        sgc.enable_and_activate_inventory(option1["sku"], [])
        for option1 in product_info["options"]
    ]
    print(res)


def get_size_table_html(size_text):
    lines = list(filter(None, map(str.strip, size_text.split("/"))))
    kv_pairs = [line.rsplit(" ", 1) for line in lines]
    headers, values = zip(*kv_pairs)
    res = "<table><thead><tr>"
    for header in headers:
        res += f"<th>{header.replace(')', '')}</th>"
    res += "</tr></thead><tbody><tr>"
    for value in values:
        res += f"<td>{value}</td>"
    res += "</tr></tbody></table>"
    return res


def update_metafields(sgc: utils.Client, product_id, product_info):
    size_text = product_info.get("size_text", "").strip()
    size_table_html = get_size_table_html(size_text)
    res = sgc.update_size_table_html_metafield(product_id, size_table_html)
    print(res)
    product_care_page_title = (
        "Product Care - " + product_info.get("product_care_option", "").strip()
    )
    res = sgc.update_product_care_page_metafield(product_id, product_care_page_title)
    print(res)


def create_products(sgc: utils.Client, product_info_list, vendor):
    ress = []
    for product_info in product_info_list:
        ress.append(create_a_product(sgc, product_info, vendor))
    return ress


def update_stocks(sgc: utils.Client, product_info_list):
    logging.info("updating inventory")
    location_id = sgc.location_id_by_name("Shop location")
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
    image_positions = []
    skuss = []
    for variant in product_info["options"]:
        if "drive_link" in variant:
            # assert variant[
            #     "drive_link"
            # ], f"no drive link for {product_info['title'], {variant}}"
            drive_id = client.drive_link_to_id(variant["drive_link"])
            image_positions.append(len(local_paths))
            skuss.append([variant["sku"]])
            local_paths += client.drive_images_to_local(
                drive_id,
                f"/Users/taro/Downloads/lememe{datetime.date.today():%Y%m%d}/",
                f"upload_{datetime.date.today():%Y%m%d}_{product_info['title'].replace('/', '_')}",
            )
    ress = []
    ress.append(client.upload_and_assign_images_to_product(product_id, local_paths))
    for image_position, skus in zip(image_positions, skuss):
        ress.append(
            client.assign_image_to_skus_by_position(product_id, image_position, skus)
        )
    return ress


def main():
    c = utils.client("lememek")
    product_info_list = product_info_list_from_sheet(c, c.sheet_id, "bags - launch")
    # product_info_list = product_info_list[:3]

    # for index, product_info in enumerate(product_info_list):
    #     if product_info["title"] == "Liberaiders PX LOGO TEE":
    #         break
    # product_info_list = product_info_list[index:]

    import pprint

    # res = create_products(c, product_info_list, vendor="lememe")
    # pprint.pprint(res)
    # update_stocks(c, product_info_list)
    for product_info in product_info_list:
        res = process_product_images(c, product_info)
        pprint.pprint(res)


if __name__ == "__main__":
    main()
