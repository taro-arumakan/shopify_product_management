import os
import shutil
import utils

images_base_dir = "/Users/taro/Downloads/3.EDITORIAL"
theme_base_dir = "/Users/taro/sc/ssil/"

import re

file_name_pattern = r"\d+|_cover"


def to_filename(client: utils.Client, filename):
    name, ext = filename.split(".")
    matches = re.findall(file_name_pattern, filename)
    name = client.shopify_compatible_name(
        "".join([m.zfill(3) if m.isdigit() else m for m in matches])
    )
    if name.startswith("_"):
        name = name[1:]
    return ".".join([name, ext])


def rename_files():
    client = utils.client("ssil")
    for dirname in os.listdir(images_base_dir):
        if dirname != ".DS_Store":
            dirpath = os.path.join(images_base_dir, dirname)
            file_prefix = client.shopify_compatible_name(
                dirname.split(".", 1)[-1].replace(" ", "_")
            )
            for filename in os.listdir(dirpath):
                if filename == ".DS_Store" or not filename.endswith((".png", ".jpg")):
                    print(f"going to delete {filename}")
                else:
                    filepath = os.path.join(dirpath, filename)
                    newfilepath = os.path.join(
                        dirpath, "_".join((file_prefix, to_filename(client, filename)))
                    )
                    print(f"renaming {filepath} to {newfilepath}")
                    shutil.move(filepath, newfilepath)


def check_files():
    client = utils.client("ssil")
    errors = []
    for dirname in os.listdir(images_base_dir):
        if dirname != ".DS_Store":
            dirpath = os.path.join(images_base_dir, dirname)
            for filename in os.listdir(dirpath):
                if filename not in [".DS_Store"]:
                    try:
                        client.file_by_file_name(filename)
                    except AssertionError as e:
                        errors.append(e)
                        print(e)
    if errors:
        raise RuntimeError("check files")


def process_dir(client: utils.Client, dirname, publish_articles=False):
    file_names = [
        filename
        for filename in sorted(os.listdir(os.path.join(images_base_dir, dirname)))
        if filename != ".DS_Store"
    ]
    article_title = dirname.split(".")[-1]
    client.article_from_image_file_names(
        theme_base_dir,
        "Editorial",
        article_title,
        file_names,
        theme_name="ssil_dev",
        publish_article=publish_articles,
    )


def process_dirs(publish_articles=False):
    client = utils.client("ssil")
    for dirname in sorted(os.listdir(images_base_dir), key=client.natural_compare):
        if dirname != ".DS_Store":
            print("processing", dirname)
            process_dir(client, dirname, publish_articles=False)


def main():
    # rename_files()      # after renaming the files, upload them to Shopify under Contents/Files
    # check_files()
    process_dirs(publish_articles=False)


if __name__ == "__main__":
    main()
