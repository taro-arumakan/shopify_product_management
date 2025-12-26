import logging
import utils

logging.basicConfig(level=logging.INFO)


def product_to_draft(product_id, testrun=True):

    client = utils.client("ssil")
    product = client.product_by_id(product_id)
    logging.info(f"Deactivating product: {product['title']} (id: {product_id})")
    if not testrun:
        client.update_product_status(product_id, "DRAFT")
