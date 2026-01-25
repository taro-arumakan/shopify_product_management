import datetime
import logging
import pathlib
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    client = utils.client("gbhjapan")
    product_inputs = client.product_inputs_by_sheet_name(
        "APPAREL 25FW (WINTER 1次 画像変更)"
    )
    product_input = product_inputs[0]
    for option1 in product_input["options"]:
        drive_link = option1["drive_link"]
        drive_id = client.drive_link_to_id(drive_link)
        skus = [option2["sku"] for option2 in option1["options"]]
        logger.info(f"going to process: {product_input['title']} - {skus} - {drive_id}")
        client.replace_images_by_skus(
            skus,
            drive_id,
        )


if __name__ == "__main__":
    main()
