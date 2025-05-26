import logging
import string
import utils

logging.basicConfig(level=logging.INFO)


def product_info_list_from_sheet(gai: utils.Client, sheet_id, sheet_name):
    start_row = 2
    column_product_attrs = dict(
        title=string.ascii_lowercase.index("c"),
        release_date=string.ascii_lowercase.index("b"),
        category=string.ascii_lowercase.index("d"),
        collection=string.ascii_lowercase.index("e"),
        description=string.ascii_lowercase.index("g"),
        product_care=string.ascii_lowercase.index("i"),
        material=string.ascii_lowercase.index("j"),
        size_text=string.ascii_lowercase.index("k"),
        made_in=string.ascii_lowercase.index("l"),
        price=string.ascii_lowercase.index("o"),
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


def parse_table_text_to_html(table_text):
    lines = filter(None, table_text.split("\n"))
    headers, valuess = [], []
    for line in lines:
        size, rest = line.split("]", 1)
        size = size.replace("[", "").strip()
        kv_pairs = rest.strip().split(" / ")
        if not headers:
            headers = [""] + [pair.split(" ")[0] for pair in kv_pairs]
        valuess.append([size] + [pair.split(" ")[1] for pair in kv_pairs])
    return utils.Client.generate_table_html(headers, valuess)


def create_a_product(
    sgc: utils.Client,
    product_info,
    vendor,
    additional_tags=None,
):
    logging.info(f'creating {product_info["title"]}')
    description_html = sgc.get_description_html(
        description=product_info["description"],
        product_care=product_info["product_care"],
        material=product_info["material"],
        size_text=product_info["size_text"],
        made_in=product_info["made_in"],
        get_size_table_html_func=parse_table_text_to_html,
    )
    tags = ",".join(
        [
            product_info["category"],
            product_info["collection"],
            product_info["release_date"],
        ]
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
                product_info, "/Users/taro/Downloads/kume20250526/", "upload_20250526_"
            )
        )
    return ress, ress2, ress3


def main():
    import pprint

    client = utils.client("kumej")
    vendor = "KUME"
    product_info_list = product_info_list_from_sheet(client, client.sheet_id, "25ss")
    product_info_list = [
        product_info
        for product_info in product_info_list
        if product_info["release_date"].startswith("5/30")
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
