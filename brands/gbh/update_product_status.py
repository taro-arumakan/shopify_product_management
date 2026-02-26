import logging
import utils

logging.basicConfig(level=logging.INFO)


def archive_products(testrun=True):

    client = utils.client("gbh")
    products = client.products_by_collection_id("324130504903")
    for product in products:
        product_id = product["id"]
        logging.info(f"Deactivating product: {product['title']} (id: {product_id})")
        if not testrun:
            client.update_product_status(product_id, "ARCHIVED")


def products_to_draft(testrun=True):
    client = utils.client("gbh")
    products = client.products_by_collection_id("311349936327")
    for product in products:
        product_id = product["id"]
        logging.info(f"Product to draft status: {product['title']} (id: {product_id})")
        if not testrun:
            client.update_product_status(product_id, "DRAFT")


if __name__ == "__main__":
    products_to_draft(testrun=False)
