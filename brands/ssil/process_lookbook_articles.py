import os
import shutil
import utils

images_base_dir = "/Users/taro/Downloads/4.LOOK BOOK/"
theme_base_dir = "/Users/taro/sc/ssil/"


def to_filename(filename):
    name, ext = filename.split(".")
    if name.isdigit():
        return ".".join([name.zfill(3), ext])
    return filename


def rename_files():
    for dirname in os.listdir(images_base_dir):
        if dirname != ".DS_Store":
            dirpath = os.path.join(images_base_dir, dirname)
            file_prefix = dirname.split(".", 1)[-1].replace(" ", "_")
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
                    else:
                        print(f"file exists: {filename}")

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
    article_title = dirname.split(".")[-1]
    thumbnail_image_name = find_thumbnail_image(file_names)
    if thumbnail_image_name.endswith("000.jpg"):
        article_image_file_names = [
            filename for filename in file_names if filename != thumbnail_image_name
        ]
    else:
        article_image_file_names = file_names

    client.article_from_image_file_names_and_product_titles(
        theme_dir=theme_base_dir,
        theme_name="ssil_dev",
        blog_title="Lookbook",
        article_title=article_title,
        thumbnail_image_file_name=thumbnail_image_name,
        article_image_file_names=article_image_file_names,
        publish_article=publish_articles,
    )


def process_dirs(publish_articles=False):
    client = utils.client("ssil")
    for dirname in sorted(os.listdir(images_base_dir), key=client.natural_compare):
        if dirname != ".DS_Store":
            print("processing", dirname)
            process_dir(client, dirname, publish_articles=publish_articles)


def main():
    # rename_files()      # after renaming the files, upload them to Shopify under Contents/Files
    # check_number_of_files()
    # check_files()
    process_dirs(publish_articles=True)


if __name__ == "__main__":
    main()
