import logging

logging.basicConfig(level=logging.INFO)

import utils

client = utils.client("blossom")
product_info_list = client.product_info_list_from_sheet("clothes(drop10)")
product_info = [p for p in product_info_list if p["title"] == "DAS DOUBLE PADDING"][0]
client.process_product_images(product_info, handle_suffix=None)
