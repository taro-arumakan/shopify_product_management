import logging
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    client = utils.client("ssil")
    products = client.products_by_query("status:'ACTIVE'")

    def compare_at_price(v):
        return int(v["compareAtPrice"] or v["price"])

    for p in products:
        logger.info(f"Processing product {p['id']} - {p['title']}")
        variant_ids, compare_at_prices, new_prices = list(
            zip(
                *(
                    [v["id"], compare_at_price(v), int(compare_at_price(v) * 0.9)]
                    for v in p["variants"]["nodes"]
                )
            )
        )
        logger.info(
            f"Updating price of {variant_ids} from {compare_at_prices} to {new_prices}"
        )
        client.update_variant_prices_by_variant_ids(
            product_id=p["id"],
            variant_ids=variant_ids,
            prices=new_prices,
            compare_at_prices=compare_at_prices,
        )


if __name__ == "__main__":
    main()
