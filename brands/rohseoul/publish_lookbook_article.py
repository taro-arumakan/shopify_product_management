import os
import pandas as pd
import string
from brands.rohseoul.client import RohseoulClient
from brands.rohseoul.article_templates import article_template_lookbook

lookbook_title = "Winter 25"
article_title = "LOOKBOOK - 25 Winter"

images_dir = (
    "/Users/taro/Downloads/drive-download-20251113T060403Z-1-001/LOOKBOOK - WINTER 25"
)
thumbnail_image_file_name = "25_Winter_lookbook_cover.jpg"

lookbook_products_sheet_id = "17tfWLDl6rcewWnwULPEz5nA7TVLz1ShEuKgILnP7xa4"
lookbook_products_sheet_name = "LOOKBOOK - WINTER 25"

lookbook_products_start_row = 3
lookbook_look_col = string.ascii_lowercase.index("b")
lookbook_number_col = string.ascii_lowercase.index("c")
lookbook_item_col = string.ascii_lowercase.index("d")
lookbook_link_col = string.ascii_lowercase.index("e")

blog_title = "Lookbook"
theme_dir = "/Users/taro/sc/rohseoul/"
theme_name = "trove bag"


lookbook_products_dicts = None


def populate_lookbook_products_dicts(client: RohseoulClient):
    global lookbook_products_dicts
    if not lookbook_products_dicts:
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
                (row["item"], row["link"])
            )
        lookbook_products_dicts = res
    return lookbook_products_dicts


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
    file_names = sorted(os.listdir(dirpath))
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
    lookbook_products_dict = populate_lookbook_products_dicts(client)
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

    client.write_to_json(
        theme_file_path, sections_dict=sections_dict, template_json=template_json
    )
    client.add_article(
        blog_title,
        article_title,
        thumbnail_image_name=thumbnail_image_file_name,
        theme_name=theme_name,
    )


if __name__ == "__main__":
    main()
