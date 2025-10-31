import os
import shutil
import utils

images_base_dir = "/Users/taro/Downloads/FIX/"
theme_base_dir = "/Users/taro/sc/ssil/"

name_title_dict = {
    "CHANYEOL": "X LINK CHAIN_S",
    "CHOI SOOYOUNG": "3 LINE HOOPS_L_C",
    "DANNIELLE": "WATER DROP E_L",
    "HAN JIEUN": "3 LINE HOOPS_S_C",
    "HYERI": "X ROW LAYER R",
    "HYUNJAE": "2 PENDANT N_BALL",
    "IRENE": "2 LINE HOOPS_S",
    "JAY PARK": "CLOVER PENDANT",
    "JOY": "3 LINE HOOPS_L_C",
    "KIM GOEUN": "RIM HOOPS",
    "KIM MINJU": "TWIST BOLD E_S",
    "LEE CHAEMIN": "TAG PENDANT",
    "LEE MINHO": "CLOVER PENDANT",
    "MEOVV ANNA": "X ROW 2 LINE HOOPS",
    "MEOVV SOOIN": "CLOVER BALL E",
    "SEO INGUK": "X DOT CHAIN",
    "SON YEJIN": "X ROW 2 LINE HOOPS,CLOVER BAND R",
    "TAEYEON": "2 PENDANT N_BALL",
    "U-KNOW": "2 PENDANT N_CLOVER",
    "WENDY": "2 PENDANT N_CLOVER",
    "YOON SEUNG AH": "X LOGO E",
    "YOONA": "LUCKY CLOVER STUDS,LUCKY CLOVER BAND R",
    "YUN EUNHYE": "3 LINE HOOPS_L_C",
}


def to_filename(filename):
    name, ext = filename.split(".")
    if name.isdigit():
        return ".".join([name.zfill(3), ext])
    return filename


def to_article_title(dirname):
    return dirname.split(".", 1)[-1]


def rename_files():
    for dirname in os.listdir(images_base_dir):
        if dirname != ".DS_Store":
            dirpath = os.path.join(images_base_dir, dirname)
            file_prefix = to_article_title(dirname).replace(" ", "_")
            for filename in os.listdir(dirpath):
                if filename == ".DS_Store" or not filename.endswith(".jpg"):
                    print(f"going to delete {filename}")
                else:
                    filepath = os.path.join(dirpath, filename)
                    newfilepath = os.path.join(
                        dirpath,
                        "_".join(("celebrities", file_prefix, to_filename(filename))),
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
                    else:
                        print(f"file exists: {filename}")

    if errors:
        raise RuntimeError("check files")


def check_products():
    client = utils.client("ssilkr")
    titles = sum([v.split(",") for v in name_title_dict.values()], [])
    for title in titles:
        try:
            client.product_by_title(title)
        except utils.NoProductsFoundException as ex:
            print(f"product not found: {title}")


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
    article_title = to_article_title(dirname)
    thumbnail_image_name = find_thumbnail_image(file_names)
    article_image_file_names = file_names
    product_titles = name_title_dict[article_title].split(",")

    client.article_from_image_file_names_and_product_titles(
        theme_dir=theme_base_dir,
        theme_name="ssil_dev",
        blog_title="Celebrities",
        article_title=article_title,
        thumbnail_image_file_name=thumbnail_image_name,
        article_image_file_names=article_image_file_names,
        product_titles=product_titles,
        publish_article=publish_articles,
    )


def process_dirs(publish_articles=False):
    client = utils.client("ssil")
    for dirname in sorted(os.listdir(images_base_dir), key=client.natural_compare):
        if dirname != ".DS_Store":
            print("processing", dirname)
            process_dir(client, dirname, publish_articles=publish_articles)


def main():
    check_products()
    rename_files()  # after renaming the files, upload them to Shopify under Contents/Files
    check_number_of_files()
    check_files()
    process_dirs(publish_articles=True)


if __name__ == "__main__":
    main()
