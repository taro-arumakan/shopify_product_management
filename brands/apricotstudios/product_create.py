import logging
import os
import string
import utils
from product_metafields_update_product_description import (
    update_product_description_metafield,
)
from product_metafields_update_size_table_html import update_size_table_html_metafield
from product_description_include_metafield_value import (
    update_description_include_metafield_value,
)
from helpers.dropbox_utils import download_and_rename_images_from_dropbox
import re

logging.basicConfig(level=logging.INFO)

IMAGES_LOCAL_DIR = "/Users/taro/Downloads/apricotstudios_20250524/"
DUMMY_PRODUCT = "gid://shopify/Product/9098700587264"


def product_info_list_from_sheet_color_and_size(
    gai: utils.Client, sheet_id, sheet_name
):
    start_row = 1
    column_product_attrs = dict(
        title=string.ascii_lowercase.index("f"),
        collection=string.ascii_lowercase.index("c"),
        category=string.ascii_lowercase.index("d"),
        release_date=string.ascii_lowercase.index("b"),
        description=string.ascii_lowercase.index("j"),
        material=string.ascii_lowercase.index("n"),
        size_text=string.ascii_lowercase.index("p"),
        made_in=string.ascii_lowercase.index("q"),
        product_main_images_link=string.ascii_lowercase.index("r"),
        product_detail_images_link=string.ascii_lowercase.index("s"),
    )
    option1_attrs = {"カラー": string.ascii_lowercase.index("u")}
    option1_attrs.update(
        variant_images_link=string.ascii_lowercase.index("t"),
    )
    option2_attrs = {"サイズ": string.ascii_lowercase.index("v")}
    option2_attrs.update(
        price=string.ascii_lowercase.index("h"),
        sku=string.ascii_lowercase.index("w"),
        stock=string.ascii_lowercase.index("y"),
    )
    return gai.to_products_list(
        sheet_id,
        sheet_name,
        start_row,
        column_product_attrs,
        option1_attrs,
        option2_attrs,
        row_filter_func=lambda row: row[string.ascii_lowercase.index("b")]
        == "5/30(2ND)",
    )


# def parse_a_size_line(size_line):
#     pattern = re.compile(r"(\S+?)：([\d.]+(?: cm)?)")
#     if not (size := pattern.findall(size_line)):
#         return ("サイズ", size_line.replace("サイズ ", "").strip())
#     return size[0]


# def parse_table_text_to_html(table_text):
#     table_text_all_sizes = filter(None, table_text.split("\n\n"))
#     header_value_pairs = []
#     for tt in table_text_all_sizes:
#         header_value_pairs.append([parse_a_size_line(line) for line in tt.split("\n")])
#     headers = [""] + [p[0] for p in header_value_pairs[0][1:]]
#     values = [[p[1] for p in pairs] for pairs in header_value_pairs]
#     return utils.Client.generate_table_html(headers, values)


def is_header(parts):
    try:
        float(parts[0])
        return False
    except ValueError:
        return True


def parse_table_text_to_html(table_text):
    lines = filter(None, table_text.split("\n"))
    tables = []
    headers = []
    rowss = []
    for line in lines:
        parts = re.split(r"\s+", line)
        if is_header(parts):
            headers.append(parts)
            rowss.append([])
        else:
            rowss[-1].append(parts)
    for header, rows in zip(headers, rowss):
        tables.append(utils.Client.generate_table_html(headers, rows))
    return tables


def text_to_html_tables_and_paragraphs(size_text):
    if "注意事項" in size_text:
        table_text, notes_text = size_text.split("注意事項", 1)
    else:
        table_text = size_text
        notes_text = ""
    size_table_htmls = parse_table_text_to_html(table_text)
    paragraphs = (
        [p.strip() for p in notes_text.split("\n") if p.strip()] if notes_text else []
    )

    html_output = "<br><br>".join(size_table_htmls)
    for paragraph in paragraphs:
        paragraph = paragraph.split()
        if paragraph:
            html_output += f"<p>{' '.join(paragraph)}</p>\n"
    return html_output


def create_a_product(sgc: utils.Client, product_info, vendor, additional_tags=None):
    logging.info(f'creating {product_info["title"]}')
    tags = ",".join(
        [
            product_info["collection"],
            product_info["category"],
            product_info["release_date"],
        ]
        + (additional_tags or [])
    )
    ress = []
    ress.append(
        sgc.create_a_product(
            product_info=product_info,
            description_html="",
            vendor=vendor,
            tags=tags,
            location_names=["Apricot Studios Warehouse"],
        )
    )
    logging.info(f'processing images for {product_info["title"]}')
    ress.append(process_images(sgc, product_info))
    ress.append(
        update_product_description_metafield(
            sgc,
            product_info["title"],
            product_info["description"],
            product_info["material"],
            product_info.get("made_in", "???"),
        )
    )
    size_text = product_info.get("size_text")
    if size_text:
        size_table_html = text_to_html_tables_and_paragraphs(size_text)
        ress.append(
            update_size_table_html_metafield(
                sgc, product_info["title"], size_table_html
            )
        )
        ress.append(
            update_description_include_metafield_value(sgc, product_info["title"])
        )
    else:
        logging.warning(f"No size information found for {product_info['title']}")


def create_products(sgc: utils.Client, product_info_list, vendor, additional_tags=None):
    ress = []
    for product_info in product_info_list:
        ress.append(
            create_a_product(sgc, product_info, vendor, additional_tags=additional_tags)
        )
    return ress
    ress2 = update_stocks(sgc, product_info_list, ["Apricot Studios Warehouse"])
    return ress, ress2


def image_prefix(title):
    return title.translate(
        str.maketrans(string.punctuation, "_" * len(string.punctuation))
    )


def download_images(dirpath, images_link, prefix, tempdir):
    if os.path.exists(dirpath):
        return [
            os.path.join(dirpath, p)
            for p in sorted(os.listdir(dirpath))
            if p.endswith((".jpg", ".jpeg", ".png"))
        ]

    return download_and_rename_images_from_dropbox(
        dirpath,
        images_link,
        prefix=prefix,
        tempdir=tempdir,
    )


def process_images(sgc: utils.Client, product_info):
    logging.info("downloading product main images")
    image_pathss = [
        download_images(
            os.path.join(
                IMAGES_LOCAL_DIR, product_info["title"], "product_main_images"
            ),
            product_info["product_main_images_link"],
            prefix=f"{image_prefix(product_info['title'])}_product_main",
            tempdir=os.path.join(IMAGES_LOCAL_DIR, "temp"),
        )
    ]
    skuss = []
    for variant in product_info["options"]:
        skus = [o2["sku"] for o2 in variant["options"]]
        logging.info(f"downloading product variant images for skus {skus}")
        image_pathss += [
            download_images(
                os.path.join(
                    IMAGES_LOCAL_DIR, product_info["title"], "variant_images", skus[0]
                ),
                variant["variant_images_link"],
                skus[0],
                tempdir=os.path.join(IMAGES_LOCAL_DIR, "temp"),
            )
        ]
        skuss.append(skus)

    import pprint

    pprint.pprint(image_pathss)
    product_id = sgc.product_id_by_title(product_info["title"])
    image_position = len(image_pathss[0])
    sgc.upload_and_assign_images_to_product(product_id, sum(image_pathss, []))
    for variant_image_paths, skus in zip(image_pathss[1:], skuss):
        print(f"assing variant image at position {image_position} to {skus}")
        sgc.assign_image_to_skus_by_position(product_id, image_position, skus)
        image_position += len(variant_image_paths)

    logging.info(f"downloading product detail images")
    detail_image_paths = download_images(
        os.path.join(IMAGES_LOCAL_DIR, product_info["title"], "product_detail_images"),
        product_info["product_detail_images_link"],
        prefix=f"{image_prefix(product_info['title'])}_product_detail",
        tempdir=os.path.join(IMAGES_LOCAL_DIR, "temp"),
    )
    sgc.upload_and_assign_description_images_to_shopify(
        product_id,
        detail_image_paths,
        DUMMY_PRODUCT,
        "https://cdn.shopify.com/s/files/1/0745/9435/3408",
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


def main():
    import pprint

    client = utils.client("apricot-studios")
    vendor = "Apricot Studios"
    product_info_list = product_info_list_from_sheet_color_and_size(
        client, client.sheet_id, "Products Master"
    )
    # for index, product_info in enumerate(product_info_list):
    #     if product_info['title'] == 'SUMMER EVERYDAY T-SHIRT':
    #         break
    # product_info_list = product_info_list[index:index+1]
    ress = create_products(
        client, product_info_list, vendor, additional_tags=["New Arrival", "25 Summer"]
    )
    pprint.pprint(ress)


if __name__ == "__main__":
    main()
