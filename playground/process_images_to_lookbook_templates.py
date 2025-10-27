import os
import shutil
import utils

images_base_dir = "/Users/taro/Downloads/EC用画像（オープン時）/4.LOOK BOOK/4.LOOK BOOK"
theme_base_dir = "/Users/taro/sc/ssil/"


def rename_dirs():
    lines = """1_21SS	21 SS
    2_21FW	21 FW
    3_21 GOLD	21 GOLD
    4_22 SPRING	22 SPRING
    5_22 SUMMER	22 SUMMER
    6_22 GOLD	22 GOLD
    7_22 FW	22 FW
    8_23 ESSENTIAL	23 ESSENTIAL
    9_23 GOLD	23 GOLD
    10_23SS 컬렉션 본문	23 SS
    11_10주년 컬렉션 본문	10th Anniversary
    12_23FW 컬렉션 본문	23 FW
    13_24SS 골드	24 SS GOLD
    14_24 SLEEK	24 SLEEK
    15_SSIL UNIVERSE 의류잡화	SSIL UNIVERSE - Apparel & Accessories
    16_14K 팬던트 컬렉션	14K Pendant
    17_뉴클로버 컬렉션(원석)	New Clover - Gemstone
    18_랩다이아몬드 컬렉션	Lab Diamond
    19_2025 1st  COLLECTION	25 1st
    20_25 GOLD COLLECTION	25 GOLD""".split(
        "\n"
    )
    mapping = {k: v for k, v in (line.split("\t") for line in lines)}
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
    elif "썸네일" in filename:
        return filename.replace("썸네일", "_cover")
    return filename.replace("&", "_")


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


def process_dir(client: utils.Client, dirname):
    file_names = [
        filename
        for filename in sorted(os.listdir(os.path.join(images_base_dir, dirname)))
    ]
    file_names = [
        filename
        for filename in file_names
        if not any(
            ("썸네일" in filename, "_cover" in filename, filename in [".DS_Store"])
        )
    ]  # skip thumbnail image
    article_title = dirname.split(". ")[-1]
    client.article_from_image_file_names(
        theme_base_dir, "Lookbook", article_title, file_names
    )


def process_dirs():
    client = utils.client("ssil")
    for dirname in sorted(os.listdir(images_base_dir)):
        if dirname != ".DS_Store":
            print("processing", dirname)
            process_dir(client, dirname)


def main():
    rename_dirs()
    rename_files()
    process_dirs()


if __name__ == "__main__":
    main()
