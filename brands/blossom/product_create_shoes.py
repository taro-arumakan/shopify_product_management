import functools
import logging
import string
import utils
from brands.blossom.product_create_clothes import process_images
from brands.blossom.update_descriptions import get_description

logging.basicConfig(level=logging.INFO)


def product_info_list_from_sheet(
    gai: utils.Client, sheet_id, sheet_name, row_filter_func=None
):
    start_row = 1  # 0 base
    column_product_attrs = dict(
        title=string.ascii_lowercase.index("b"),
        tags=string.ascii_lowercase.index("c"),
        price=string.ascii_lowercase.index("e"),
        description=string.ascii_lowercase.index("g"),
        product_care=string.ascii_lowercase.index("i"),
        material=string.ascii_lowercase.index("j"),
        size_text=string.ascii_lowercase.index("k"),
        made_in=string.ascii_lowercase.index("l"),
    )
    option1_attrs = {"Color": string.ascii_lowercase.index("m")}
    option1_attrs.update(
        drive_link=string.ascii_lowercase.index("n"),
    )
    option2_attrs = {"Size": string.ascii_lowercase.index("o")}
    option2_attrs.update(
        sku=string.ascii_lowercase.index("p"),
        stock=string.ascii_lowercase.index("q"),
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


def create_a_product(sgc: utils.Client, product_info, vendor, locations):
    logging.info(f'creating {product_info["title"]}')
    description_html = get_description(
        product_info.get("description", ""),
        product_info.get("material", ""),
        product_info.get("made_in", ""),
    )
    tags = product_info["tags"]
    res = sgc.create_a_product(product_info, vendor, description_html, tags, locations)
    product_id = res[0]["id"]
    update_metafields(sgc, product_id, product_info)


def get_size_table_html(client, size_text):
    pairs = map(str.strip, size_text.split("/"))
    names, values = zip(*(pair.rsplit(" ", 1) for pair in pairs))
    return client.generate_table_html(names, [values])


def update_metafields(sgc: utils.Client, product_id, product_info):
    size_text = product_info.get("size_text", "").strip()
    size_table_html = get_size_table_html(sgc, size_text)
    res = sgc.update_size_table_html_metafield(product_id, size_table_html)
    print(res)
    if product_care := product_info.get("product_care", "").strip():
        res = sgc.update_product_care_metafield(
            product_id, sgc.text_to_simple_richtext(product_care)
        )
        print(res)


def main():
    c = utils.client("blossomhcompany")
    product_info_list = product_info_list_from_sheet(c, c.sheet_id, "shoes")

    # for index, product_info in enumerate(product_info_list):
    #     if product_info["title"] == "Liberaiders PX LOGO TEE":
    #         break
    # product_info_list = product_info_list[index:]

    c.sanity_check_product_info_list(
        product_info_list=product_info_list,
        text_to_html_func=functools.partial(get_size_table_html, c),
    )

    import pprint

    location = "Blossom Warehouse"
    for product_info in product_info_list:
        create_a_product(c, product_info, vendor="blossom", locations=[location])

    c.update_stocks(product_info_list, location)
    process_images(c, product_info_list)
    c.publish_products(product_info_list)


if __name__ == "__main__":
    main()
