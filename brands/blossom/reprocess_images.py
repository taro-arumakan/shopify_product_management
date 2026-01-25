import logging

logging.basicConfig(level=logging.INFO)

import utils

client = utils.client("blossom")
product_inputs = client.product_inputs_by_sheet_name("clothes(drop10)")
product_input = [p for p in product_inputs if p["title"] == "DAS DOUBLE PADDING"][0]
client.process_product_images(product_input, handle_suffix=None)
