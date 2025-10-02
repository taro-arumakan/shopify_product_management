import logging
import utils
import time
from brands.blossom.product_create_clothes import product_info_list_from_sheet

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("blossomhcompany")

    product_info_list = product_info_list_from_sheet(client, client.sheet_id, "clothes")
    for index, product_info in enumerate(product_info_list):
        if product_info["title"] == "SEER WHOLEGARMENT KNIT":
            break
    product_info_list = product_info_list[index:]

    for product_info in product_info_list:
        title = product_info["title"]
        product = client.product_by_title(title)
        product_id = product["id"]
        tags = product["tags"] + ["New Arrival"]
        tags = ",".join(tags)
        time.sleep(1)
        logging.info(f"updating {product_id} to {tags}")
        client.update_product_tags(product_id, tags)


if __name__ == "__main__":
    main()
