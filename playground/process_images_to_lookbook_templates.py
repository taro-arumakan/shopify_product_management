import copy
import json
import os
import shutil

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


def to_sections_dict(dirname):
    base_attrs = {
        "type": "image",
        "settings": {
            "image_link": "",
            "margin_top": 10,
            "margin_bottom": 10,
            "max_width": 600,
            "mobile_max_width": 400,
        },
    }
    sections = {}
    section_count = 0
    for i, filename in enumerate(
        sorted(os.listdir(os.path.join(images_base_dir, dirname)))
    ):
        if "썸네일" in filename or filename in ".DS_Store":  # skip thumbnail image
            continue
        if (i - 1) % 10 == 9:
            if section_count:
                sections.update(section)
            section_count += 1
            section = {
                f"images_list_{section_count}": {
                    "type": "images-list",
                    "blocks": {},
                    "block_order": [],
                    "name": "t:sections.images_list.presets.images_list.name",
                    "settings": {
                        "color_scheme": "",
                        "image_position": "center",
                        "overlay_color": "#000000",
                        "overlay_opacity": 0,
                    },
                }
            }

        block_name = f"image_{str(i).zfill(3)}"
        block = {block_name: copy.deepcopy(base_attrs)}
        block[block_name]["settings"]["image"] = f"shopify://shop_images/{filename}"
        section[f"images_list_{section_count}"]["blocks"].update(block)
        section[f"images_list_{section_count}"]["block_order"].append(block_name)
    return sections


def dirname_to_lookbook_name(dirname):
    return dirname.split(". ")[-1].replace(" ", "_").replace("&", "_")


def write_to_json(dirname, sections_dict):
    with open("playground/lookbook_template.txt") as f:
        output_dict = json.loads(f.read())
    output_dict["sections"].update(sections_dict)
    output_dict["order"] += sections_dict.keys()
    with open(
        os.path.join(
            theme_base_dir,
            f"templates/article.lookbook-{dirname_to_lookbook_name(dirname)}.json",
        ),
        "w",
    ) as of:
        of.write(json.dumps(output_dict, indent=2))


def generate_jsons():
    for dirname in sorted(os.listdir(images_base_dir)):
        if dirname != ".DS_Store":
            print("processing", dirname)
            sections_dict = to_sections_dict(dirname)
            write_to_json(dirname, sections_dict)


def main():
    # rename_dirs()
    # rename_files()
    generate_jsons()


if __name__ == "__main__":
    main()
