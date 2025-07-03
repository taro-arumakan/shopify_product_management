import logging
import string
import utils

logging.basicConfig(level=logging.INFO)


def product_info_lists_from_sheet(
    gai: utils.Client, sheet_id, sheet_name, handle_suffix
):
    start_row = 2
    column_product_attrs = dict(
        title=string.ascii_lowercase.index("e"),
        status=string.ascii_lowercase.index("a"),
        release_date=string.ascii_lowercase.index("c"),
        collection=string.ascii_lowercase.index("g"),
        category=string.ascii_lowercase.index("h"),
        description=string.ascii_lowercase.index("r"),
        size_text=string.ascii_lowercase.index("u"),
        material=string.ascii_lowercase.index("v"),
        made_in=string.ascii_lowercase.index("w"),
    )
    column_variant_attrs = {"カラー": string.ascii_lowercase.index("j")}
    column_variant_attrs.update(
        sku=string.ascii_lowercase.index("f"),
        price=string.ascii_lowercase.index("m"),
        stock=string.ascii_lowercase.index("n"),
        drive_link=string.ascii_lowercase.index("p"),
    )
    return gai.to_products_list(
        sheet_id,
        sheet_name,
        start_row,
        column_product_attrs,
        column_variant_attrs,
        handle_suffix=handle_suffix,
    )


def get_size_table_html(size_text):
    lines = list(filter(None, map(str.strip, size_text.split("\n"))))
    kv_pairs = [line.rsplit(" ", 1) for line in lines]
    kv_pairs = [pair if len(pair) == 2 else ["Weight", pair[0]] for pair in kv_pairs]
    headers, values = zip(*kv_pairs)
    res = "<table><thead><tr>"
    for header in headers:
        res += f"<th>{header.replace(')', '')}</th>"
    res += "</tr></thead><tbody><tr>"
    for value in values:
        res += f"<td>{value}</td>"
    res += "</tr></tbody></table>"
    return res


def get_description_html(sgc: utils.Client, description, material, size_text, made_in):
    product_care = """革表面に跡や汚れなどが残る場合がありますが、天然皮革の特徴である不良ではございませんのでご了承ください。また、時間経過により金属の装飾や革の色が変化する場合がございますが、製品の欠陥ではありません。あらかじめご了承ください。
1: 熱や直射日光に長時間さらされると革に変色が生じることがありますのでご注意ください。
2: 変形の恐れがありますので、無理のない内容量でご使用ください。
3: 水に弱い素材です。濡れた場合は柔らかい布で水気を除去した後、乾燥させてください。
4: 使用しないときはダストバッグに入れ、涼しく風通しのいい場所で保管してください。
5: アルコール、オイル、香水、化粧品などにより製品が損傷することがありますので、ご使用の際はご注意ください。"""
    return sgc.get_description_html(
        description,
        product_care,
        material,
        size_text,
        made_in,
        get_size_table_html_func=get_size_table_html,
    )


def create_products(client: utils.Client, product_info_list, vendor):
    description_html_map = {
        product_info["title"]: get_description_html(
            client,
            product_info["description"],
            product_info["material"],
            product_info["size_text"],
            product_info["made_in"],
        )
        for product_info in product_info_list
        if product_info["description"]
        and product_info["size_text"]
        and product_info["made_in"]
    }
    ress = []
    for product_info in product_info_list:
        description_html = description_html_map[product_info["title"]]
        tags = ",".join(
            [
                product_info["release_date"],
                product_info["collection"],
                product_info["category"],
                "New Arrival",
            ]
        )
        ress.append(
            client.create_a_product(
                product_info,
                vendor,
                description_html=description_html,
                tags=tags,
                location_names=["Shop location"],
            )
        )
    return ress


def update_stocks(sgc: utils.Client, product_info_list):
    logging.info("updating inventory")
    location_id = sgc.location_id_by_name("Shop location")
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
    handle_suffix = None
    import pprint

    client = utils.client("rohseoul")
    product_info_list = product_info_lists_from_sheet(
        client, client.sheet_id, "25SS 4차 1ST", handle_suffix
    )
    ress = create_products(client, product_info_list, client.shop_name)
    pprint.pprint(ress)
    ress = update_stocks(client, product_info_list)
    pprint.pprint(ress)
    ress = []
    for product_info in product_info_list:
        ress.append(
            client.process_product_images(
                product_info,
                "/Users/taro/Downloads/rohseoul20250701/",
                "upload_20250701_",
                handle_suffix,
            )
        )
    pprint.pprint(ress)


if __name__ == "__main__":
    main()
