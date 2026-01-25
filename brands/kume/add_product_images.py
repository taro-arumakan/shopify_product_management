import logging
import utils

logging.basicConfig(level=logging.INFO)

client = utils.client("kumej")

product_inputs = client.product_inputs_by_sheet_name("25ss")
product_input = product_inputs[-1]

product_handle = client.product_title_to_handle(product_input["title"], "white")
product_id = client.product_id_by_handle(product_handle)
drive_links, skuss = client.populate_drive_ids_and_skuss(product_input)

res = client.add_product_images(
    product_id,
    drive_links[0],
    "/Users/taro/Downloads/kume20250710/",
    f"upload_20250710_{skuss[0][0]}_",
)
