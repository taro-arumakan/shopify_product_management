import json
import logging
import os
import re
from brands.archivepke.client import ArchivepkeClient

logging.basicConfig(level=logging.INFO)

THEME_NAME = "2025 スエード15％OFF"

THEME_BASE_DIR = "/Users/taro/sc/archive-epke/"
COVER_PAGE_TEMPLATE_NAME = "lookbook"


def copy_template(client, page_info):
    template_path = os.path.join(
        THEME_BASE_DIR, "templates", f"page.{page_info['templateSuffix']}.json"
    )
    with open(template_path) as f:
        contents = f.read()
    contents = contents.replace("main-page", "main-article")
    copy_to_template_path = client.article_template_path(
        THEME_BASE_DIR, "Lookbook", page_info["title"]
    )
    with open(copy_to_template_path, "w") as f:
        f.write(contents)


def find_thumbnail_image_name(page_info):
    template_path = os.path.join(
        THEME_BASE_DIR, "templates", f"page.{page_info['templateSuffix']}.json"
    )
    with open(template_path) as f:
        content = f.read()
        # Remove C-style comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        d = json.loads(content)
    for section in d["sections"].values():
        if section["type"] == "image-with-text-overlay":
            return section["settings"]["image"]


def create_redirect(client: ArchivepkeClient, page_info, handle=""):
    client.create_url_redirect(
        f"/pages/{page_info['handle']}", f"/blogs/lookbook/{handle}"
    )


def process_page(client: ArchivepkeClient, page_info):
    if page_info["templateSuffix"] != COVER_PAGE_TEMPLATE_NAME:
        copy_template(client, page_info)
        article_title = page_info["title"]
        thumbnail_image_file_name = find_thumbnail_image_name(page_info).rsplit("/", 1)[
            -1
        ]
        res = client.add_article(
            "Lookbook",
            article_title,
            thumbnail_image_name=thumbnail_image_file_name,
            theme_name=THEME_NAME,
        )
    else:
        res = None
    create_redirect(
        client=client, page_info=page_info, handle=res["handle"] if res else ""
    )


def page_sort_key(item):
    season_order = {"Spring": 2, "SUMMER": 3, "Autumn": 4, "WINTER": 5}

    title = item["title"]
    parts = title.split()
    if len(parts) == 1:
        # Just 'LOOKBOOK' with no year/season
        return (0, 0)  # Put it before all
    elif len(parts) == 4:
        # 'LOOKBOOK {season1 season2} {year}'
        year = int(parts[-1])
        season = season_order.get(parts[-2], 5)
        return (year, season)
    else:
        # Unknown pattern fallback, put at end
        return (9999, 9999)


def main():
    client = ArchivepkeClient()
    pages = client.pages_by_title("LOOKBOOK*", sort_key="TITLE")
    pages = sorted(pages, key=page_sort_key)
    for page in pages:
        process_page(client, page)


if __name__ == "__main__":
    main()
