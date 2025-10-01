import datetime
import logging
import string
import utils
from brands.blossom.update_descriptions import get_description


logging.basicConfig(level=logging.WARNING)


def product_info_list_from_sheet(
    gai: utils.Client, sheet_id, sheet_name, row_filter_func=None
):
    start_row = 1
    column_product_attrs = dict(
        title=string.ascii_lowercase.index("a"),
        tags=string.ascii_lowercase.index("b"),
        price=string.ascii_lowercase.index("d"),
        description=string.ascii_lowercase.index("f"),
        product_care=string.ascii_lowercase.index("h"),
        material=string.ascii_lowercase.index("i"),
        size_text=string.ascii_lowercase.index("j"),
        made_in=string.ascii_lowercase.index("k"),
    )
    option1_attrs = {"Color": string.ascii_lowercase.index("l")}
    option1_attrs.update(
        drive_link=string.ascii_lowercase.index("m"),
    )
    option2_attrs = {"Size": string.ascii_lowercase.index("n")}
    option2_attrs.update(
        sku=string.ascii_lowercase.index("o"),
        stock=string.ascii_lowercase.index("p"),
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
    print(res)


def update_metafields(sgc: utils.Client, product_id, product_info):
    size_text = product_info.get("size_text", "").strip()
    size_table_html = sgc.formatted_size_text_to_html_table(size_text)
    res = sgc.update_size_table_html_metafield(product_id, size_table_html)
    print(res)
    if product_care := product_info.get("product_care", "").strip():
        res = sgc.update_product_care_metafield(
            product_id, sgc.text_to_simple_richtext(product_care)
        )
        print(res)


def process_images(client: utils.Client, product_info_list):
    for product_info in product_info_list:
        res = client.process_product_images(
            product_info,
            local_dir=f"/Users/taro/Downloads/blossom{datetime.date.today():%Y%m%d}/",
            local_prefix=f"upload_{datetime.date.today():%Y%m%d}",
        )
        logging.debug(res)


def publish(client: utils.Client, product_info_list):
    for product_info in product_info_list:
        product_id = client.product_id_by_title(product_info["title"])
        client.activate_and_publish_by_product_id(product_id)


def main():
    c = utils.client("blossomhcompany")
    product_info_list = product_info_list_from_sheet(c, c.sheet_id, "clothes")

    product_info_list = [
        pi
        for pi in product_info_list
        if pi["title"] not in ["GENTO SHIRRING TOP", "GENTO BALLOON SKIRT"]
    ]
    # for index, product_info in enumerate(product_info_list):
    #     if product_info["title"] == "GAEIL SUEDE BEMUDA PANTS":
    #         break
    # product_info_list = product_info_list[index:]

    c.sanity_check_product_info_list(
        product_info_list=product_info_list,
        text_to_html_func=c.formatted_size_text_to_html_table,
    )

    location = "Blossom Warehouse"
    for product_info in product_info_list:
        create_a_product(c, product_info, vendor="blossom", locations=[location])
    c.update_stocks(product_info_list, location)
    process_images(c, product_info_list)
    publish(c, product_info_list)


if __name__ == "__main__":
    main()
