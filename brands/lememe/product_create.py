import datetime
import logging
import pathlib
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
        filter_color=string.ascii_lowercase.index("n"),
        drive_link=string.ascii_lowercase.index("o"),
        sku=string.ascii_lowercase.index("r"),
        stock=string.ascii_lowercase.index("s"),
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


def create_a_product(sgc: utils.Client, product_info, vendor, locations):
    logging.info(f'creating {product_info["title"]}')
    description_html = get_description(
        product_info["description"],
        product_info.get("material", ""),
        product_info.get("made_in", ""),
    )
    tags = product_info["tags"]
    options = populate_option(product_info, "Color")
    res = sgc.create_a_product(product_info, vendor, description_html, tags, locations)
    res = sgc.product_create(
        title=product_info["title"],
        description_html=description_html,
        vendor=vendor,
        tags=tags,
        option_lists=options,
    )
    product_id = res["id"]
    update_metafields(sgc, product_id, product_info)


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


def update_description(sgc: utils.Client, product_info_list):
    for pi in product_info_list:
        if "別売" in pi["description"]:
            description_html = get_description(
                pi["description"],
                pi.get("material", ""),
                pi.get("made_in", ""),
            )

            product_id = sgc.product_id_by_title(pi["title"])
            logging.info(f'updating description for {pi["title"]}')
            sgc.update_product_description(product_id, description_html)


def main():
    c = utils.client("lememek")
    location = "Shop location"

    product_info_list = product_info_list_from_sheet(c, c.sheet_id, "bags - launch")
    update_description(c, product_info_list)
    # product_info_list = product_info_list[:3]

    # for index, product_info in enumerate(product_info_list):
    #     if product_info["title"] == "Liberaiders PX LOGO TEE":
    #         break
    # product_info_list = product_info_list[index:]

    # for product_info in product_info_list:
    #     create_a_product(c, product_info, "lememe", [location])
    #     c.process_product_images(product_info)
    # c.update_stocks(product_info_list, location)
    # c.publish_products(product_info_list)


if __name__ == "__main__":
    main()
