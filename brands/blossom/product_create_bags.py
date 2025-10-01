import logging
import string
import utils
from brands.blossom.product_create_clothes import create_a_product, process_images


logging.basicConfig(level=logging.INFO)


def product_info_list_from_sheet(
    gai: utils.Client, sheet_id, sheet_name, row_filter_func=None
):
    start_row = 1
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


def main():
    c = utils.client("blossomhcompany")
    product_info_list = product_info_list_from_sheet(c, c.sheet_id, "bags")

    # for index, product_info in enumerate(product_info_list):
    #     if product_info["title"] == "Liberaiders PX LOGO TEE":
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
    c.publish_products(product_info_list)


if __name__ == "__main__":
    main()
