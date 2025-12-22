"""
Scheduled for 2025-01-01 00:00 JST
"""

import logging
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_new_price(variant):
    compare_at_price = variant["compareAtPrice"] or variant["price"]
    return int(int(compare_at_price) * 0.95)


def main():
    client = utils.client("lememe")
    products = client.products_by_query()
    new_prices_by_variant_id = {
        v["id"]: get_new_price(v) for p in products for v in p["variants"]["nodes"]
    }
    client.update_variant_prices_by_dict(
        products, new_prices_by_variant_id=new_prices_by_variant_id, testrun=False
    )


if __name__ == "__main__":
    main()
