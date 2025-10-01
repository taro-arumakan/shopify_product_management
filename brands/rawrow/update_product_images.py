import string
import utils


def product_info_list_from_sheet(gai: utils.Client, sheet_id, sheet_name):
    start_row = 2
    column_product_attrs = dict(
        title=string.ascii_lowercase.index("b"),
        tags=string.ascii_lowercase.index("c"),
        description=string.ascii_lowercase.index("g"),
        product_care=string.ascii_lowercase.index("i"),
        material=string.ascii_lowercase.index("j"),
        size_text=string.ascii_lowercase.index("k"),
        made_in=string.ascii_lowercase.index("l"),
    )
    option1_attrs = {"カラー": string.ascii_lowercase.index("m")}
    option1_attrs.update(
        drive_link=string.ascii_lowercase.index("o"),
        price=string.ascii_lowercase.index("e"),
        sku=string.ascii_lowercase.index("q"),
        stock=string.ascii_lowercase.index("r"),
    )
    return gai.to_products_list(
        sheet_id, sheet_name, start_row, column_product_attrs, option1_attrs
    )


def main():
    import logging

    logging.basicConfig(level=logging.INFO)

    import pprint

    client = utils.client("rawrowr")
    product_info_list = product_info_list_from_sheet(
        client, client.sheet_id, "20250211_v3"
    )
    ress = []
    for product_info in product_info_list:
        if product_info["title"] == 'R TRUNK LITE ep.3 72L / 27"':
            ress.append(client.process_product_images(product_info))
    pprint.pprint(ress)


if __name__ == "__main__":
    main()
