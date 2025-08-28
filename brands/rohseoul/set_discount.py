import logging
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    client = utils.client("rohseoul")
    products = client.products_by_collection_id("451368026371")
    for p in products:
        logger.info(f"Processing product {p['id']} - {p['title']}")
        for variant in p["variants"]["nodes"]:
            compare_at_price = variant["compareAtPrice"] or variant["price"]
            price = int(int(compare_at_price) * 0.95)
            logger.info(
                f"Updating price of {variant['id']} from {compare_at_price} to {price}"
            )
            client.update_variant_attributes(
                product_id=p["id"],
                variant_id=variant["id"],
                attribute_names=["price", "compareAtPrice"],
                attribute_values=[str(price), str(compare_at_price)],
            )


if __name__ == "__main__":
    main()
