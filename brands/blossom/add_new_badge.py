import logging
import utils
import time

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("blossomhcompany")

    product_inputs = client.product_inputs_by_sheet_name("clothes")
    for index, product_input in enumerate(product_inputs):
        if product_input["title"] == "SEER WHOLEGARMENT KNIT":
            break
    product_inputs = product_inputs[index:]

    for product_input in product_inputs:
        title = product_input["title"]
        product = client.product_by_title(title)
        product_id = product["id"]
        time.sleep(1)
        logging.info(f"adding NEW to {product_id}")
        client.update_badges_metafield(product_id, ["NEW"])


if __name__ == "__main__":
    main()
