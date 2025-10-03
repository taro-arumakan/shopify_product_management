import copy
import datetime
import logging
import pytz
import string
import utils
from brands.gbh.get_size_table_html import size_table_html_from_size_dict_space_pairs

logging.basicConfig(level=logging.INFO)


def product_info_list_from_sheet_color_and_size(
    gai: utils.Client, sheet_id, sheet_name
):
    start_row = 1
    column_product_attrs = dict(
        title=string.ascii_lowercase.index("f"),
        collection=string.ascii_lowercase.index("c"),
        category=string.ascii_lowercase.index("d"),
        category2=string.ascii_lowercase.index("e"),
        release_date=string.ascii_lowercase.index("b"),
        description=string.ascii_lowercase.index("q"),
        product_care=string.ascii_lowercase.index("s"),
        material=string.ascii_lowercase.index("u"),
        made_in=string.ascii_lowercase.index("v"),
    )
    option1_attrs = {"カラー": string.ascii_lowercase.index("g")}
    option1_attrs.update(
        drive_link=string.ascii_lowercase.index("o"),
    )
    option2_attrs = {"サイズ": string.ascii_lowercase.index("h")}
    option2_attrs.update(
        price=string.ascii_lowercase.index("l"),
        sku=string.ascii_lowercase.index("i"),
        stock=string.ascii_lowercase.index("m"),
        size_text=string.ascii_lowercase.index("t"),
    )
    return gai.to_products_list(
        sheet_id,
        sheet_name,
        start_row,
        column_product_attrs,
        option1_attrs,
        option2_attrs,
    )


def create_a_product(
    sgc: utils.Client,
    product_info,
    vendor,
    locations,
    additional_tags=None,
):
    logging.info(f'creating {product_info["title"]}')
    size_texts = {
        option2["サイズ"]: option2["size_text"]
        for option1 in product_info["options"]
        for option2 in option1["options"]
    }
    description_html = sgc.get_description_html(
        description=product_info["description"],
        product_care=product_info["product_care"],
        material=product_info["material"],
        size_text=size_texts or product_info["size_text"],
        made_in=product_info["made_in"],
        get_size_table_html_func=size_table_html_from_size_dict_space_pairs,
    )
    tags = ",".join(
        [
            product_info["category"],
            product_info["category2"],
            product_info["release_date"],
        ]
        + (additional_tags or [])
    )
    return sgc.create_a_product(
        product_info=product_info,
        vendor=vendor,
        description_html=description_html,
        tags=tags,
        location_names=locations,
    )


def merge_size_texts(product_info):
    product_info = copy.deepcopy(product_info)
    # uniquify size and size texts, keeping the order
    sizes, size_texts = map(
        dict.fromkeys,
        zip(
            *[
                (o2["サイズ"], o2["size_text"])
                for o1 in product_info["options"]
                for o2 in o1["options"]
            ]
        ),
    )
    size_text = "\n".join(f"[{size}] {st}" for size, st in zip(sizes, size_texts))
    product_info["size_text"] = size_text
    return product_info


def main():
    import pprint

    client = utils.client("gbhjapan")
    vendor = "GBH"
    location = "Shop location"

    product_info_list = product_info_list_from_sheet_color_and_size(
        client, client.sheet_id, "APPAREL 25FW (FALL 2次)"
    )
    product_info_list = [merge_size_texts(pi) for pi in product_info_list]
    skus_exists = ["FLEECE MOUNTAIN JACKET", "BOUCLE RAGLAN KNIT"]
    titles_exists = ["WOOL CREW NECK KNIT", "WOOL V-NECK SWEATER"]
    product_info_list = [
        pi for pi in product_info_list if pi["title"] not in skus_exists + titles_exists
    ]

    # client.check_size_texts(
    #     product_info_list, text_to_html_func=client.formatted_size_text_to_html_table, raise_on_error=True
    # )

    client.sanity_check_product_info_list(
        product_info_list, text_to_html_func=client.formatted_size_text_to_html_table
    )

    for product_info in product_info_list:
        create_a_product(
            client,
            product_info,
            vendor,
            [location],
            additional_tags=["New Arrival", "25FW", "25FW_Fall_2nd"],
        )

    client.update_stocks(product_info_list, location)

    for product_info in product_info_list:
        client.process_product_images(product_info)

    # scheduled_time = pytz.timezone("Asia/Tokyo").localize(
    #     datetime.datetime(2025, 10, 9, 0, 0, 0)
    # )
    # client.publish_products(product_info_list, scheduled_time=scheduled_time)


if __name__ == "__main__":
    main()
