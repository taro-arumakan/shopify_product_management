import logging
import string
import utils
import re

logging.basicConfig(level=logging.INFO)

IMAGES_LOCAL_DIR = "/Users/taro/Downloads/rawrowr20250418/"
DUMMY_PRODUCT = "gid://shopify/Product/8773753700593"
SHOPIFY_FILE_URL_PREFIX = "https://cdn.shopify.com/s/files/1/0726/9187/6081/"

additional_punctuation_chars = "‘’“” "
punctuation_chrs = string.punctuation + additional_punctuation_chars
punctuation_translator = str.maketrans(punctuation_chrs, "_" * len(punctuation_chrs))


def get_product_name(title):
    if title.startswith("R TRUNK"):
        res = title
    else:
        res = f"R BAG {title}"
    res = res.replace("_", "/")
    if r'" ' in res:
        res = res[: res.find('" ') + 1]
    res = re.sub(r"\s*/\s*", " / ", res)
    # res = re.sub(r'\s+\d+$', '', res)
    name_map = {"R BAG TRAVELOG CROSS": "R BAG TRAVELOG CROSS 904"}
    return name_map.get(res, res)


def main():
    client = utils.client("rawrowr")
    folders = client.list_folders(parent_folder_id="1ijec5ijfvFLvpzZGW7KmM7D0tQkUDky7")
    for f in folders:
        dir_id = f["id"]
        name = get_product_name(f["name"])
        if name.startswith("R TRUNK LITE ep.3 72L"):
            prefix = name.translate(punctuation_translator)
            print("processing", name)
            product = client.product_by_query(
                f"title:{name}*", additional_fields=["descriptionHtml"]
            )
            if not product["descriptionHtml"]:
                print(f"product {name} has no description, prrocessing")
                local_paths = client.drive_images_to_local(
                    dir_id, IMAGES_LOCAL_DIR, filename_prefix=f"{prefix}_"
                )
                if local_paths:
                    product_id = client.product_id_by_title(name.replace("_", "/"))
                    print(f"upload {len(local_paths)} images to {product_id}")
                    client.upload_and_assign_description_images_to_shopify(
                        product_id, local_paths, DUMMY_PRODUCT, SHOPIFY_FILE_URL_PREFIX
                    )


if __name__ == "__main__":
    main()
