import copy
import json
import os
import shutil
import utils

images_base_dir = "/Users/taro/Downloads/4.LOOK BOOK/"
theme_base_dir = "/Users/taro/sc/ssil/"


def rename_dirs():
    lines = """1_21SS	21 SS
    2_21FW	21 FW
    3_21 GOLD	21 GOLD
    4_22 SPRING	22 SPRING
    5_22 SUMMER	22 SUMMER
    6_22 GOLD	22 GOLD
    7_22 FW	22 FW
    7_23 ESSENTIAL	23 ESSENTIAL
    8_23 GOLD	23 GOLD
    8_23SS 컬렉션 본문	23 SS
    9_10주년 컬렉션 본문	10th Anniversary
    10_23FW 컬렉션 본문	23 FW
    12_24SS 골드	24 SS GOLD
    13_24 SLEEK	24 SLEEK
    14_SSIL UNIVERSE 의류잡화	SSIL UNIVERSE - Apparel & Accessories
    15_14K 팬던트 컬렉션	14K Pendant
    16_뉴클로버 컬렉션(원석)	New Clover - Gemstone
    17_랩다이아몬드 컬렉션	Lab Diamond
    18_2025 1st  COLLECTION	25 1st
    19_25 GOLD COLLECTION	25 GOLD""".split(
        "\n"
    )
    mapping = {k.strip(): v.strip() for k, v in (line.split("\t") for line in lines)}
    for k, v in mapping.items():
        sequence = k.split("_")[0]
        mapping[k] = f"{sequence.zfill(2)}. {v}"

    for p in os.listdir(images_base_dir):
        if p != ".DS_Store":
            shutil.move(
                os.path.join(images_base_dir, p),
                os.path.join(images_base_dir, mapping[p]),
            )


def to_filename(filename):
    name, ext = filename.split(".")
    if name.isdigit():
        return ".".join([name.zfill(3), ext])
    return filename


def rename_files():
    for dirname in os.listdir(images_base_dir):
        if dirname != ".DS_Store":
            dirpath = os.path.join(images_base_dir, dirname)
            file_prefix = dirname.split(" ", 1)[-1].replace(" ", "_")
            for filename in os.listdir(dirpath):
                if filename == ".DS_Store" or not filename.endswith(".jpg"):
                    print(f"going to delete {filename}")
                else:
                    filepath = os.path.join(dirpath, filename)
                    newfilepath = os.path.join(
                        dirpath, "_".join((file_prefix, to_filename(filename)))
                    )
                    print(f"renaming {filepath} to {newfilepath}")
                    shutil.move(filepath, newfilepath)


def check_number_of_files():
    for dirname in os.listdir(images_base_dir):
        if dirname != ".DS_Store":
            dirpath = os.path.join(images_base_dir, dirname)
            file_names = [
                filename
                for filename in os.listdir(dirpath)
                if filename not in [".DS_Store"]
            ]
            print(dirname, len(file_names))


def check_files():
    # TODO too excessive. possibly retrieve files in bulk with article_title* and check for names
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


def find_thumbnail_image(filenames):
    for filename in filenames:
        if "_cover" in filename:
            return filename
    return filenames[0]


def process_dir(client: utils.Client, dirname, publish_articles=False):
    file_names = [
        filename
        for filename in sorted(os.listdir(os.path.join(images_base_dir, dirname)))
        if filename != ".DS_Store"
    ]
    article_title = dirname.split(". ")[-1]
    thumbnail_image_name = find_thumbnail_image(file_names)
    client.article_from_image_file_names(
        theme_base_dir,
        "Lookbook",
        article_title,
        thumbnail_image_file_name=thumbnail_image_name,
        article_image_file_names=file_names,
        theme_name="ssil_dev",
        publish_article=publish_articles,
    )


def process_dirs(publish_articles=False):
    client = utils.client("ssil")
    for dirname in sorted(os.listdir(images_base_dir), key=client.natural_compare):
        if dirname != ".DS_Store":
            print("processing", dirname)
            process_dir(client, dirname, publish_articles=publish_articles)


def main():
    # rename_dirs()
    # rename_files()      # after renaming the files, upload them to Shopify under Contents/Files
    # check_files()
    # process_dirs(publish_articles=True)
    check_number_of_files()


if __name__ == "__main__":
    main()
