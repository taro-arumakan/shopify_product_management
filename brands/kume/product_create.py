import logging
import string
import utils

logging.basicConfig(level=logging.INFO)


def product_info_list_from_sheet(gai: utils.Client, sheet_id, sheet_name):
    start_row = 4
    column_product_attrs = dict(
        title=string.ascii_lowercase.index("d"),
        release_date=string.ascii_lowercase.index("c"),
        category=string.ascii_lowercase.index("e"),
        collection=string.ascii_lowercase.index("f"),
        description=string.ascii_lowercase.index("h"),
        product_care=string.ascii_lowercase.index("j"),
        material=string.ascii_lowercase.index("k"),
        size_text=string.ascii_lowercase.index("l"),
        made_in=string.ascii_lowercase.index("m"),
        price=string.ascii_lowercase.index("p"),
    )
    option1_attrs = {"カラー": string.ascii_lowercase.index("q")}
    option1_attrs.update(
        drive_link=string.ascii_lowercase.index("r"),
    )
    option2_attrs = {"サイズ": string.ascii_lowercase.index("s")}
    option2_attrs.update(
        sku=string.ascii_lowercase.index("t"),
        stock=string.ascii_lowercase.index("u"),
    )
    return gai.to_products_list(
        sheet_id,
        sheet_name,
        start_row,
        column_product_attrs,
        option1_attrs,
        option2_attrs,
    )


def parse_line_to_header_and_values(line: str):
    size, rest = line.split("]", 1)
    size = size.replace("[", "").strip()
    kv_pairs = list(map(str.strip, rest.strip().split("/")))
    headers = [""] + [pair.split(" ")[0] for pair in kv_pairs]
    values = [size] + [pair.split(" ", 1)[1].strip() for pair in kv_pairs]
    return headers, values


def parse_table_text_to_html(table_text):
    lines = filter(None, table_text.split("\n"))
    valuess = []
    for line in lines:
        headers, values = parse_line_to_header_and_values(line)
        valuess.append(values)
    return utils.Client.generate_table_html(headers, valuess)


def heading_headers_values_to_html(heading, headers, valuess):
    res = utils.Client.generate_table_html(headers, valuess)
    res = f"<h3>{heading}</h3>{res}"
    return res


def parse_headings_and_table_text_to_html(size_text):
    lines = filter(None, size_text.split("\n"))
    headings, headerss, valuesss = [], [], []
    for line in lines:
        size_or_heading, rest = line.split("]", 1)
        rest = rest.strip()
        if not rest:
            headings.append(size_or_heading.replace("[", ""))
        else:
            headers, values = parse_line_to_header_and_values(line)
            if len(headings) > len(headerss):
                headerss.append(headers)
                valuesss.append([])
            valuesss[-1].append(values)
    return "\n<br><br>\n\n".join(
        [
            heading_headers_values_to_html(heading, headers, valuess)
            for heading, headers, valuess in zip(headings, headerss, valuesss)
        ]
    )


def parse_size_text_to_html(size_text):
    lines = filter(None, size_text.split("\n"))
    with_headings = False
    for line in lines:
        _, rest = line.split("]", 1)
        rest = rest.strip()
        if not rest:
            with_headings = True
            break
    if not with_headings:
        return parse_table_text_to_html(size_text)
    else:
        return parse_headings_and_table_text_to_html(size_text)


def create_a_product(
    sgc: utils.Client,
    product_info,
    vendor,
    additional_tags=["New Arrival"],
):
    logging.info(f'creating {product_info["title"]}')
    description_html = sgc.get_description_html(
        description=product_info["description"],
        product_care=product_info["product_care"],
        material=product_info["material"],
        size_text=product_info["size_text"],
        made_in=product_info["made_in"],
        get_size_table_html_func=parse_size_text_to_html,
    )
    tags = ",".join(
        list(map(str.strip, product_info["category"].split(" AND ")))
        + [product_info["collection"]]
        + (additional_tags or [])
    )
    return sgc.create_a_product(
        product_info=product_info,
        vendor=vendor,
        description_html=description_html,
        tags=tags,
        location_names=["KUME Warehouse", "Envycube Warehouse"],
    )


def update_stocks(sgc: utils.Client, product_info_list, location_name):
    logging.info("updating inventory")
    location_id = sgc.location_id_by_name(location_name)
    sku_stock_map = {}
    for product_info in product_info_list:
        sku_stock_map.update(sgc.get_sku_stocks_map(product_info))
    ress = []
    for sku, stock in sku_stock_map.items():
        ress.append(
            sgc.set_inventory_quantity_by_sku_and_location_id(sku, location_id, stock)
        )
    return ress


def create_products(
    sgc: utils.Client,
    product_info_list,
    vendor,
    additional_tags=None,
):
    ress = []
    for product_info in product_info_list:
        ress.append(
            create_a_product(
                sgc,
                product_info,
                vendor,
                additional_tags=additional_tags,
            )
        )

    logging.info("updating inventory")
    ress2 = update_stocks(sgc, product_info_list, "KUME Warehouse")

    ress3 = []
    logging.info("processing product images")
    for product_info in product_info_list:
        ress3.append(
            sgc.process_product_images(
                product_info,
                "/Users/taro/Downloads/kume20250729/",
                local_prefix="upload_20250729_",
            )
        )
    # return ress, ress2, ress3


def main():
    import pprint

    client = utils.client("kumej")
    vendor = "KUME"
    product_info_list = product_info_list_from_sheet(
        client, client.sheet_id, "25FW_9月1日"
    )

    product_info_list = [
        product_info
        for product_info in product_info_list
        if product_info["release_date"] == "2025-09-01"
    ]
    ress = create_products(
        client,
        product_info_list,
        vendor,
        additional_tags=["New Arrival"],
    )
    pprint.pprint(ress)


if __name__ == "__main__":
    main()
