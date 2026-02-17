import logging
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    client = utils.client("ssil")
    products = client.products_by_query("tag:'26_gold_line'")
    new_prices_by_variant_id = {
        v["id"]: int(int(v["compareAtPrice"]) * 0.95)
        for p in products
        for v in p["variants"]["nodes"]
    }
    client.update_product_prices_by_dict(
        products, new_prices_by_variant_id=new_prices_by_variant_id, testrun=False
    )


if __name__ == "__main__":
    main()
