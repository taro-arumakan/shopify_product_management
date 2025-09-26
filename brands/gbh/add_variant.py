import datetime
import logging
import utils
from brands.gbh.product_create_apparel import (
    product_info_list_from_sheet_color_and_size,
)

logging.basicConfig(level=logging.INFO)

client = utils.client("gbhjapan")
processing_skus = ["APB3CD070NYFF"]
product_title_map = {"MERINO WOOL HIGHNECK CARDIGAN": "MERINOWOOL HIGHNECK CARDIGAN"}

product_info_list = product_info_list_from_sheet_color_and_size(
    client, client.sheet_id, "APPAREL 25FW (FALL 1次)"
)
for product_info in product_info_list:
    for option1 in product_info["options"]:
        for option2 in option1["options"]:
            if option2["sku"] in processing_skus:
                logging.info(
                    f"going to process: {option2['sku']} - {product_info['title']}"
                )
                product_id = client.product_id_by_title(
                    product_title_map.get(product_info["title"], product_info["title"])
                )
                drive_links, skuss = client.populate_drive_ids_and_skuss(product_info)
                for drive_link, skus in zip(drive_links, skuss):
                    if any(ps in skus for ps in processing_skus):
                        logging.info(f"  processing sku: {skus} - {drive_link}")
                        res = client.add_product_images(
                            product_id,
                            drive_link,
                            f"/Users/taro/Downloads/gbh{datetime.date.today():%Y%m%d}/",
                            f"upload_{datetime.date.today():%Y%m%d}_{skuss[0][0]}_",
                        )

                        new_media_ids = [
                            m["id"] for m in res[-1]["productCreateMedia"]["media"]
                        ]

                        client.variants_add(
                            product_id,
                            skus,
                            [],
                            [new_media_ids[0]],
                            ["カラー", "サイズ"],
                            [[option1["カラー"], "FREE"]],
                            [option2["price"]],
                            [option2["stock"]],
                            client.location_id_by_name("Shop location"),
                        )
