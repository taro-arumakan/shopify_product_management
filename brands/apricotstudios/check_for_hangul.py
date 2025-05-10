import os
import re
import pytesseract
from PIL import Image
import utils
from helpers.dropbox_utils import download_images_from_dropbox
from brands.apricotstudios.product_create import (
    product_info_list_from_sheet_color_and_size,
)

korean_pattern = re.compile(r"[\uac00-\ud7a3]")


def contains_korean_characters(text):
    return bool(korean_pattern.search(text))


import logging

logging.basicConfig(level=logging.INFO)

LOCAL_ROOT = "/Users/taro/Downloads/apricotstudios_20250509_details"


def download():
    client = utils.client("apricot-studios")
    product_info_list = product_info_list_from_sheet_color_and_size(
        client, client.sheet_id, "Products Master"
    )

    os.makedirs(LOCAL_ROOT, exist_ok=True)
    for product_info in product_info_list:
        output_dir = f"{LOCAL_ROOT}/{product_info['title']}"
        download_images_from_dropbox(
            product_info["product_detail_images_link"], output_dir
        )


def is_model_info_image(image):
    extracted_text = pytesseract.image_to_string(image, lang="eng")
    return "model info" in extracted_text.lower()


def check_image_for_korean(file_path):
    try:
        image = Image.open(file_path)
        if is_model_info_image(image):
            return "model_info"
        extracted_text = pytesseract.image_to_string(image, lang="kor")
        return contains_korean_characters(extracted_text)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")


def check_all():
    image_dirs = [
        f"{LOCAL_ROOT}/{p}" for p in sorted(os.listdir(LOCAL_ROOT)) if p != ".DS_Store"
    ]
    result = {}
    for d in image_dirs:
        image_paths = [f"{d}/{p}" for p in sorted(os.listdir(d))]
        for path in image_paths:
            result.setdefault(check_image_for_korean(path), []).append(path)
    print("model_info")
    for path in result["model_info"]:
        print(path)

    print()
    print()
    print("possible hangul")
    for path in result[True]:
        print(path)


def main():
    download()
    check_all()


if __name__ == "__main__":
    main()
