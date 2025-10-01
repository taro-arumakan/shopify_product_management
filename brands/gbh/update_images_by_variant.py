import datetime
import logging
import pathlib
import utils
from brands.gbh.product_create_apparel import (
    product_info_list_from_sheet_color_and_size,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_IMAGE_PREFIX = f"uplaod{datetime.date.today():%Y%m%d}_gbh"
IMAGES_LOCAL_DIR = f"{pathlib.Path.home()}/Downloads/{datetime.date.today():%Y%m%d}/"


def main():
    client = utils.client("gbhjapan")
    product_info_list = product_info_list_from_sheet_color_and_size(
        client, client.sheet_id, "APPAREL 25FW (FALL 1次)"
    )
    for index, pi in enumerate(product_info_list):
        if pi["title"] == "SKIRT WRAP BELT":
            break
    product_info_list = product_info_list[index:]

    for product_info in product_info_list:
        for option1 in product_info["options"]:
            drive_link = option1["drive_link"]
            drive_id = client.drive_link_to_id(drive_link)
            skus = [option2["sku"] for option2 in option1["options"]]
            if "APB3KN040SBFF" not in skus:
                logger.info(
                    f"going to process: {product_info['title']} - {skus} - {drive_id}"
                )
                client.replace_images_by_skus(
                    skus,
                    drive_id,
                    IMAGES_LOCAL_DIR,
                    download_filename_prefix=f"{UPLOAD_IMAGE_PREFIX}_{skus[0]}_",
                )


if __name__ == "__main__":
    main()
