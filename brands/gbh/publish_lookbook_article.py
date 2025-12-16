import json
import logging
import os
import re
from brands.gbh.client import GbhClient

logging.basicConfig(level=logging.INFO)

THEME_NAME = "prod2025.12-8"

THEME_BASE_DIR = "/Users/taro/sc/gbhjapan/"

thumbnail_image_file_name = "LOOKBOOK_2025_FW_1.jpg"
lookbook_images_dir = "/Users/taro/Downloads/25fw LOOKBOOK, 動画(EC用)"
article_title = "LOOKBOOK 2025 FW"

def main():
    client = GbhClient()


    file_names = sorted(
        (p for p in os.listdir(lookbook_images_dir) if p.endswith(".jpg")),
        key=client.natural_compare,
    )
    client.article_from_image_file_names_and_product_titles(
        theme_dir=THEME_BASE_DIR,
        theme_name=THEME_NAME,
        blog_title="Lookbook",
        article_title=article_title,
        thumbnail_image_file_name=thumbnail_image_file_name,
        article_image_file_names=file_names,
        article_json_template=article_json_template(),
        publish_article=True,
    )

def article_json_template():
    return r"""{
  "wrapper": "div.fixed-width-wrapper",
  "sections": {
    "main": {
      "type": "main-article",
      "disabled": true,
      "settings": {
        "color_scheme": "",
        "show_image": true,
        "enable_parallax": true,
        "image_size": "medium",
        "content_width": "xs",
        "show_date": true,
        "show_category": true,
        "show_author": true,
        "show_share_buttons": true,
        "show_sticky_bar": true,
        "toolbar_color_scheme": ""
      }
    }
  },
  "order": [
    "main"
  ]
}
"""


if __name__ == "__main__":
    main()