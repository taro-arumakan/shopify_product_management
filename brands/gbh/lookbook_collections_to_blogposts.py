import json
import logging
import os
import re
from brands.gbh.client import GbhClient

logging.basicConfig(level=logging.INFO)

THEME_NAME = "10.10.1"

THEME_BASE_DIR = "/Users/taro/sc/gbhjapan/"


def copy_template(client: GbhClient, page_info, template_type="collection"):
    template_path = os.path.join(
        THEME_BASE_DIR,
        "templates",
        f"{template_type}.{page_info['templateSuffix']}.json",
    )
    with open(template_path) as f:
        contents = f.read()
    contents = contents.replace(f"main-{template_type}", "main-article")
    # Remove C-style comments
    contents = re.sub(r"/\*.*?\*/", "", contents, flags=re.DOTALL)
    d = json.loads(contents)
    if "template_type" == "collection":
        d["sections"].pop("collection-banner")
        d["order"].remove("collection-banner")

    copy_to_template_path = client.article_template_path(
        THEME_BASE_DIR, "Lookbook", page_info["title"]
    )
    with open(copy_to_template_path, "w") as f:
        f.write(json.dumps(d, indent=2))


def find_thumbnail_image_name(page_info, template_type="collection"):
    template_path = os.path.join(
        THEME_BASE_DIR,
        "templates",
        f"{template_type}.{page_info['templateSuffix']}.json",
    )
    with open(template_path) as f:
        content = f.read()
        # Remove C-style comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        d = json.loads(content)
    for section in d["sections"].values():
        if section["type"] == "image-with-text-overlay":
            return section["settings"]["image"]
    for section in d["sections"].values():
        if section["type"] == "images-list":
            return list(section["blocks"].values())[0]["settings"]["image"]


def create_redirect(
    client: GbhClient, collection_info, handle, template_type="collection"
):
    client.create_url_redirect(
        f"/{template_type}s/{collection_info['handle']}", f"/blogs/lookbook/{handle}"
    )


def process_collection(client: GbhClient, collection_info, template_type):
    article_title = collection_info["title"]
    logging.info(f"processing: {template_type} - {article_title}")
    copy_template(client, collection_info, template_type)

    thumbnail_image_file_name = find_thumbnail_image_name(
        collection_info, template_type
    ).rsplit("/", 1)[-1]
    res = client.add_article(
        "Lookbook",
        article_title,
        thumbnail_image_name=thumbnail_image_file_name,
        theme_name=THEME_NAME,
    )

    create_redirect(
        client=client,
        collection_info=collection_info,
        handle=res["handle"],
        template_type=template_type,
    )


def page_sort_key(item):
    season_order = {
        "SPRING": 2,
        "SS": 2,
        "SUMMER": 3,
        "RESORT": 3.5,
        "FALL": 4,
        "FW": 4,
        "PRE-WINTER": 4.5,
        "WINTER": 5,
    }

    title = item["title"]
    parts = title.split()
    assert len(parts) == 3, parts
    year = int(parts[-2])
    season = season_order.get(parts[-1].upper(), 5)
    return (year, season)


def main():
    client = GbhClient()
    collections = client.collections_by_query("title:LOOKBOOK*")
    collections = sorted(collections, key=page_sort_key)
    for collection in collections:
        process_collection(client, collection, template_type="collection")
    pages = client.pages_by_query("title:LOOKBOOK*")
    pages = sorted(pages, key=page_sort_key)
    for page in pages:
        process_collection(client, page, template_type="page")


if __name__ == "__main__":
    main()
