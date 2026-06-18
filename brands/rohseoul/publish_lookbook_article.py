"""
Expects all relevant image files uploaded already.
Download the images dir from Google Drive.
Rename files as required (in the format 26_Resort_LB__1-_1.jpg).
Upload the files, then run the script.
"""

import functools
import os
import pandas as pd
import re
import string
from brands.rohseoul.client import RohseoulClient
from brands.rohseoul.article_templates import article_template_lookbook

lookbook_title = "Resort 26"
article_title = f"LOOKBOOK - {lookbook_title}"

images_dir = f"/Users/taro/Downloads/LOOKBOOK - {lookbook_title.upper()}"
thumbnail_image_file_name = (
    f"LOOKBOOK_-_{lookbook_title.upper().replace(" ", "_")}_COVER_IMAGE.jpg"
)

LP_SHEET_ID = "17tfWLDl6rcewWnwULPEz5nA7TVLz1ShEuKgILnP7xa4"
LP_SHEET_NAME = f"LOOKBOOK - {lookbook_title.upper()}"

lookbook_products_start_row = 3
lookbook_look_col = string.ascii_lowercase.index("b")
lookbook_number_col = string.ascii_lowercase.index("c")
lookbook_item_col = string.ascii_lowercase.index("d")
lookbook_link_col = string.ascii_lowercase.index("e")

blog_title = "Lookbook"
theme_dir = "/Users/taro/sc/rohseoul/"
theme_name = "prod"


def variant_color(variant):
    for so in variant["selectedOptions"]:
        if so["name"] == "カラー":
            return so["value"]


@functools.lru_cache(maxsize=128)
def products_by_title_cached(client: RohseoulClient, product_title):
    return client.products_by_query(f"""title:"{product_title}" AND status:'ACTIVE'""")


@functools.lru_cache(maxsize=128)
def lookup_product_variant_url(client: RohseoulClient, product_and_color):
    # Pattern explanation:
    # ^(.*)         -> Group 1: Matches everything from the start (greedy)
    # \s+           -> Matches the whitespace separator
    # ([A-Z].*)     -> Group 2: Matches a capital letter followed by anything to the end
    pattern = r"^(.*)\s+([A-Z].*)$"

    match = re.search(pattern, product_and_color)
    if match:
        title = match.group(1)
        color = match.group(2)
        print(f"Title: {title} | Color: {color}")
        products = products_by_title_cached(client, title)
        for p in products:
            for v in p["variants"]["nodes"]:
                if variant_color(v).lower() == color.lower():
                    return f"https://rohseoul.jp/products/{p['handle']}?variant={v['id'].rsplit("/", 1)[-1]}"


def populate_lookbook_products_dicts(
    client: RohseoulClient, lookbook_products_sheet_id, lookbook_products_sheet_name
):
    res = {}
    rows = client.worksheet_rows(
        lookbook_products_sheet_id, lookbook_products_sheet_name
    )[lookbook_products_start_row:]
    rows = [
        [
            r[lookbook_look_col],
            r[lookbook_number_col],
            r[lookbook_item_col],
            r[lookbook_link_col],
        ]
        for r in rows
    ]
    df = pd.DataFrame(rows, columns=["look", "number", "item", "link"])
    fill_columns = ["look", "number"]
    df[fill_columns] = df[fill_columns].replace("", pd.NA)
    df[fill_columns] = df[fill_columns].ffill()
    df["number"] = df["number"].astype(int)
    res = {}
    for _, row in df.iterrows():
        res.setdefault(f"{row['look']}-{row['number']}", []).append(
            (
                row["item"],
                row["link"] or lookup_product_variant_url(client, row["item"]),
            )
        )
    return res


def populate_product_content(lookbook_products_dict, look, number):
    products = lookbook_products_dict[f"{look}-{number}"]
    ress = []
    for product, link in products:
        res = "<p>"
        if link:
            res += f'<a href="{link}">'
        res += f"{product}"
        if link:
            res += "</a>"
        res += "</p>"
        ress.append(res)
    return "".join(ress)


def process_a_subdir(client: RohseoulClient, subdir):
    section_title = subdir  # #1, #2, ...
    section_seq = section_title.replace("#", "")
    dirpath = os.path.join(images_dir, subdir)
    file_names = [f for f in sorted(os.listdir(dirpath)) if f.endswith(".jpg")]
    file_names = [client.shopify_sanitized_filename(fn) for fn in file_names]
    res = {
        f"rich_text_{section_seq}": {
            "type": "rich-text",
            "blocks": {
                "heading_HJHmHt": {
                    "type": "heading",
                    "settings": {"text": section_title, "heading_tag": "h4"},
                }
            },
            "block_order": ["heading_HJHmHt"],
            "settings": {
                "color_scheme": "",
                "separate_section_with_border": True,
                "content_width": "sm",
                "text_position": "center",
                "remove_vertical_spacing": False,
            },
        }
    }
    images_section = {
        f"multi_column_{section_seq}": {
            "type": "multi-column",
            "blocks": {},
            "block_order": [],
            "settings": {
                "color_scheme": "",
                "separate_section_with_border": False,
                "columns_per_row": 3,
                "stack_on_mobile": True,
                "overlap_image": False,
                "content_alignment": "start",
                "text_alignment": "start",
                "spacing": "md",
                "subheading": "",
                "title": "",
                "content": "",
            },
        },
    }
    lookbook_products_dict = populate_lookbook_products_dicts(
        client, LP_SHEET_ID, LP_SHEET_NAME
    )
    for i, filename in enumerate(file_names):
        block = {
            f"image_with_text_{i}": {
                "type": "image_with_text",
                "settings": {
                    "image": f"shopify://shop_images/{filename}",
                    "title": f"{section_title}-{i+1}",
                    "heading_tag": "h5",
                    "content": populate_product_content(
                        lookbook_products_dict, look=section_title, number=i + 1
                    ),
                    "link_url": "",
                    "link_text": "",
                },
            },
        }
        images_section[f"multi_column_{section_seq}"]["blocks"].update(block)
        images_section[f"multi_column_{section_seq}"]["block_order"].append(
            f"image_with_text_{i}"
        )
    res.update(images_section)
    return res


def main():
    client = RohseoulClient()
    template_json = article_template_lookbook()
    template_json = template_json.replace("${LOOKBOOK_TITLE}", lookbook_title)

    sections_dict = {}
    for subdir in sorted(os.listdir(images_dir)):
        if subdir.startswith("#"):
            print("processing", subdir)
            section_dict = process_a_subdir(client, subdir)
            sections_dict.update(section_dict)
    theme_file_path = client.article_template_path(theme_dir, blog_title, article_title)

    print("writing to", theme_file_path)
    client.write_to_json(
        theme_file_path, sections_dict=sections_dict, template_json=template_json
    )
    print(f"adding article {article_title} to {theme_name}")
    client.add_article(
        blog_title,
        article_title,
        thumbnail_image_name=client.shopify_sanitized_filename(
            thumbnail_image_file_name
        ),
        theme_name=theme_name,
    )


if __name__ == "__main__":
    main()
