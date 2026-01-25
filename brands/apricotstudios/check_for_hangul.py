import logging

logging.basicConfig(level=logging.INFO)

import os
import re
import easyocr
import pytesseract
from PIL import Image
import utils
from helpers.dropbox_utils import download_images_from_dropbox


LOCAL_ROOT = "/Users/taro/Downloads/apricotstudios_20250524"

korean_pattern = re.compile(r"[\uac00-\ud7a3]")


def contains_korean_characters(text):
    return bool(korean_pattern.search(text))


def is_model_info_image_pytesseract(image):
    extracted_text = pytesseract.image_to_string(image, lang="eng")
    return "model info" in extracted_text.lower()


def check_image_for_korean_pytesseract(image):
    extracted_text = pytesseract.image_to_string(image, lang="kor")
    return contains_korean_characters(extracted_text)


def is_model_info_image_eo(file_path, reader=None):
    reader = reader or easyocr.Reader(["en"])
    results = reader.readtext(file_path, detail=0)
    return "model info" in " ".join(results).lower()


def check_image_for_korean_eo(file_path, reader=None):
    reader = reader or easyocr.Reader(["ko"])
    results = reader.readtext(
        file_path,
        detail=0,
        text_threshold=0.99,  # ↑ from default 0.7 (strict confidence)
        #   low_text=0.5,         # ↑ from default 0.4 (tighter text regions)
        #   contrast_ths=0.3,     # ↑ from default 0.1 (ignore low-contrast areas)
        #    link_threshold=0.5,  # ↑ from default 0.4 (strict word grouping)
        allowlist="".join([chr(c) for c in range(0xAC00, 0xD7A3 + 1)]),
    )  # Hangul-only))
    return contains_korean_characters("".join(results))


def check_pytesseract(paths):
    logging.info("Checking images with pytesseract...")
    result = {}
    for path in paths:
        logging.info(f"Checking {path}")
        try:
            image = Image.open(path)
            if is_model_info_image_pytesseract(image):
                result.setdefault("model_info", []).append(path)
            elif check_image_for_korean_pytesseract(image):
                result.setdefault(True, []).append(path)
        except Exception as e:
            print(f"Error processing {path} with pytesseract: {e}")
    return result


def check_eo(paths):
    logging.info("Checking images with EasyOCR...")
    reader_en = easyocr.Reader(["en"])
    reader_ko = easyocr.Reader(["ko"])
    result = {}
    for path in paths:
        logging.info(f"Checking {path}")
        try:
            if is_model_info_image_eo(path, reader_en):
                result.setdefault("model_info", []).append(path)
            elif check_image_for_korean_eo(path, reader_ko):
                result.setdefault(True, []).append(path)
        except Exception as e:
            print(f"Error processing {path} with EasyOCR: {e}")
    return result


def check_all_both(paths):
    result_pytesseract = check_pytesseract(paths)
    print("!!! pytesseract !!!")
    print("model_info")
    for path in result_pytesseract["model_info"]:
        print(path)

    print()
    print("possible hangul")
    for path in result_pytesseract[True]:
        print(path)

    # print()
    # print()
    # result_eo = check_eo(paths)
    # print("!!! EasyOCR !!!")
    # print("model_info")
    # for path in result_eo["model_info"]:
    #     print(path)
    # print()
    # print("possible hangul")
    # for path in result_eo[True]:
    #     print(path)


def check_images():
    image_paths = sorted(
        sum(
            [
                [
                    os.path.join(dirpath, fn)
                    for fn in filenames
                    if fn.endswith((".jpg", ".jpeg", ".png"))
                ]
                for dirpath, _, filenames in os.walk(LOCAL_ROOT)
                if dirpath.endswith("product_detail_images")
            ],
            [],
        )
    )
    check_all_both(image_paths)


def download():
    client = utils.client("apricot-studios")
    product_inputs = client.product_inputs_by_sheet_name("Products Master")

    os.makedirs(LOCAL_ROOT, exist_ok=True)
    for product_input in product_inputs:
        output_dir = f"{LOCAL_ROOT}/{product_input['title']}"
        download_images_from_dropbox(
            product_input["product_detail_images_link"], output_dir
        )


def main():
    # download()
    check_images()


if __name__ == "__main__":
    main()
