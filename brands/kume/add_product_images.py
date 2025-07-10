import logging
import utils
from brands.kume.product_create import product_info_list_from_sheet

logging.basicConfig(level=logging.INFO)

client = utils.client("kumej")

product_info_list = product_info_list_from_sheet(client, client.sheet_id, "25ss")
product_info = product_info_list[-1]

product_handle = client.product_title_to_handle(product_info["title"], "white")
product_id = client.product_id_by_handle(product_handle)
drive_links, skuss = client.populate_drive_ids_and_skuss(product_info)

res = client.add_product_images(
    product_id,
    drive_links[0],
    "/Users/taro/Downloads/kume20250710/",
    f"upload_20250710_{skuss[0][0]}_",
)
