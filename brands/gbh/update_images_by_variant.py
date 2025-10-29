import datetime
import logging
import pathlib
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    client = utils.client("gbhjapan")
    product_info_list = client.product_info_list_from_sheet(
        "APPAREL 25FW (WINTER 1次 画像変更)"
    )
    product_info = product_info_list[0]
    for option1 in product_info["options"]:
        drive_link = option1["drive_link"]
        drive_id = client.drive_link_to_id(drive_link)
        skus = [option2["sku"] for option2 in option1["options"]]
        logger.info(f"going to process: {product_info['title']} - {skus} - {drive_id}")
        client.replace_images_by_skus(
            skus,
            drive_id,
        )


if __name__ == "__main__":
    main()
