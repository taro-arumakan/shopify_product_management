import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("blossomhcompany")
    products = client.products_by_query(
        "tag_not:'25_drop7' AND tag_not:'25_drop8' AND status:'ACTIVE'"
    )
    client.revert_variant_prices(products, testrun=True)


if __name__ == "__main__":
    main()
