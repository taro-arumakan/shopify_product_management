import datetime
import logging
import pytz
import utils

logging.basicConfig(level=logging.INFO)

from brands.liberaiders.product_create import product_info_list_from_sheet


def main():
    client = utils.client("liberaiders")
    product_info_list = product_info_list_from_sheet(
        client, client.sheet_id, "Product Master"
    )
    product_info_list = product_info_list[2:]
    publications = client.publications()
    for product_info in product_info_list:
        product = client.product_by_title(product_info["title"])
        if not product["media"]["nodes"]:
            logging.info(f"not publishing {product_info['title']}")
            continue
        params = {"product_id": product["id"]}
        for publication in publications:
            params["publication_id"] = publication["id"]
            client.publish_by_product_id_and_publication_id(**params)
        client.update_product_status(product["id"], "ACTIVE")


if __name__ == "__main__":
    main()
