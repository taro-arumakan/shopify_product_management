import json
import logging
import os
import re
from brands.rohseoul.client import RohseoulClient

logging.basicConfig(level=logging.INFO)

THEME_NAME = "trove bag"

THEME_BASE_DIR = "/Users/taro/sc/rohseoul/"


def copy_template(client, page_info):
    template_path = os.path.join(
        THEME_BASE_DIR, "templates", f"collection.{page_info['templateSuffix']}.json"
    )
    with open(template_path) as f:
        contents = f.read()
    contents = contents.replace("main-collection", "main-article")
    # Remove C-style comments
    contents = re.sub(r"/\*.*?\*/", "", contents, flags=re.DOTALL)
    d = json.loads(contents)
    d["sections"].pop("collection-banner")
    d["order"].remove("collection-banner")

    copy_to_template_path = client.article_template_path(
        THEME_BASE_DIR, "Lookbook", page_info["title"]
    )
    with open(copy_to_template_path, "w") as f:
        f.write(json.dumps(d, indent=2))


def find_thumbnail_image_url(collection_info):
    return collection_info["image"]["url"]


def create_redirect(client: RohseoulClient, collection_info, handle):
    client.create_url_redirect(
        f"/collections/{collection_info['handle']}", f"/blogs/lookbook/{handle}"
    )


def process_collection(client: RohseoulClient, collection_info):
    copy_template(client, collection_info)
    article_title = collection_info["title"]
    media_url = find_thumbnail_image_url(collection_info)
    res = client.add_article_with_media_url(
        "Lookbook",
        article_title,
        thumbnail_media_url=media_url,
        theme_name=THEME_NAME,
    )
    create_redirect(
        client=client, collection_info=collection_info, handle=res["handle"]
    )


def page_sort_key(item):
    season_order = {
        "SPRING": 2,
        "SUMMER": 3,
        "RESORT": 3.5,
        "FALL": 4,
        "PRE-WINTER": 4.5,
        "WINTER": 5,
    }
    category_order = {"CAMPAIGN": 1, "LOOKBOOK": 2}

    title = item["title"]
    parts = title.split()
    assert len(parts) == 4, parts
    # '{category} - {year} {season}'
    category = category_order.get(parts[0].upper(), 99)
    year = int(parts[-2])
    season = season_order.get(parts[-1].upper(), 5)
    return (year, season, category)


def main():
    client = RohseoulClient()
    collections = client.collections_by_query("title:LOOKBOOK* OR title:Campaign*")
    collections = sorted(collections, key=page_sort_key)
    for collection in collections:
        # print(collection['title'])
        process_collection(client, collection)


if __name__ == "__main__":
    main()
