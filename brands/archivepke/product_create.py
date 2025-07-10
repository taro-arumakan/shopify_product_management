import logging
import re
import string
import utils

logging.basicConfig(level=logging.INFO)


def product_info_lists_from_sheet(
    gai: utils.Client, sheet_id, sheet_title, handle_suffix=None
):
    start_row = 2  # 0 base
    column_product_attrs = dict(
        title=string.ascii_lowercase.index("d"),
        release_date=string.ascii_lowercase.index("c"),
        collection=string.ascii_lowercase.index("f"),
        category=string.ascii_lowercase.index("h"),
        description=string.ascii_lowercase.index("q"),
        size_text=string.ascii_lowercase.index("t"),
        material=string.ascii_lowercase.index("u"),
        made_in=string.ascii_lowercase.index("v"),
    )
    column_variant_attrs = {"カラー": string.ascii_lowercase.index("i")}
    column_variant_attrs.update(
        sku=string.ascii_lowercase.index("e"),
        price=string.ascii_lowercase.index("l"),
        drive_link=string.ascii_lowercase.index("o"),
        stock=string.ascii_lowercase.index("m"),
    )
    return gai.to_products_list(
        sheet_id,
        sheet_title,
        start_row,
        column_product_attrs,
        column_variant_attrs,
        handle_suffix=handle_suffix,
    )


def get_size_table_html(size_text):
    kv_pairs = list(map(str.strip, re.split("[\n/]", size_text)))
    headers, values = zip(*[kv_pair.split(" ") for kv_pair in kv_pairs])
    return generate_table_html(headers, [values])


def generate_table_html(headers, rows):
    html = """
        <table border="1" style="border-collapse: collapse; text-align: left;">
            <thead>
                <tr>"""
    for header in headers:
        html += f"""
                    <th>{header}</th>"""
    html += """
                </tr>
            </thead>
            <tbody>"""

    for row in rows:
        html += """
                <tr>"""
        for v in row:
            html += f"""
                    <td>{v}</td>"""
        html += """
                </tr>"""

    html += """
            </tbody>
        </table>"""

    return html


def get_description_html(sgc: utils.Client, description, material, size_text, made_in):
    product_care = """水や汗にさらされると、湿気によるカビや変色の恐れがあります。そのため、雨などに濡れないようご注意ください。

長時間水分に触れた場合は、革が水分を吸収する前にタオルで余分な水分を取り除いてください。内側に新聞紙などを詰め、風通しの良い場所で保管してください。"""
    return sgc.get_description_html(
        description,
        product_care,
        material,
        size_text,
        made_in,
        get_size_table_html_func=get_size_table_html,
    )


def create_a_product(sgc: utils.Client, product_info, vendor):
    description_html = get_description_html(
        sgc,
        product_info["description"],
        product_info["material"],
        product_info["size_text"],
        product_info["made_in"],
    )
    tags = ",".join(
        [
            product_info["release_date"],
            product_info["collection"],
            product_info["category"],
            "New Arrival",
        ]
    )
    sgc.create_a_product(
        product_info,
        vendor,
        description_html=description_html,
        tags=tags,
        location_names=["Archivépke Warehouse", "Envycube Warehouse"],
    )


def update_stocks(sgc: utils.Client, product_info_list):
    logging.info("updating inventory")
    location_id = sgc.location_id_by_name("Archivépke Warehouse")
    sku_stock_map = {
        variant_info["sku"]: variant_info["stock"]
        for product_info in product_info_list
        for variant_info in product_info["options"]
    }
    return [
        sgc.set_inventory_quantity_by_sku_and_location_id(sku, location_id, stock)
        for sku, stock in sku_stock_map.items()
    ]


def main():
    client = utils.client("archive-epke")
    product_info_list = product_info_lists_from_sheet(
        client, client.sheet_id, "2025.7 SPOT Release"
    )
    product_info_list = [
        pr for pr in product_info_list if pr["title"] != "Knotted layer bag"
    ]
    import pprint

    ress = []
    for product_info in product_info_list:
        pprint.pprint(product_info)
        res = create_a_product(client, product_info, "archive-epke")
        ress.append(res)
    pprint.pprint(ress)

    res = update_stocks(client, product_info_list)
    pprint.pprint(res)

    ress = []
    for product_info in product_info_list:
        ress.append(
            client.process_product_images(
                product_info,
                "/Users/taro/Downloads/archivépke20250710/",
                "upload_20250710_",
            )
        )
    pprint.pprint(ress)


if __name__ == "__main__":
    main()
