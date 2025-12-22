"""
Scheduled for 2025-01-05 23:59 JST
"""

import logging
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    client = utils.client("lememe")
    products = client.products_by_query()
    client.revert_variant_prices(products, testrun=False)


if __name__ == "__main__":
    main()
