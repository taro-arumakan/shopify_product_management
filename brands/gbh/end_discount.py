import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("gbh")
    products = client.products_by_query("tag:'APPAREL' AND status:'ACTIVE'")
    for product in products:
        for variant in product["variants"]["nodes"]:
            if variant["price"] != variant["compareAtPrice"]:
                client.update_variant_prices_by_variant_ids(
                    product_id=product["id"],
                    variant_ids=[variant["id"]],
                    prices=[variant["compareAtPrice"]],
                    compare_at_prices=[variant["compareAtPrice"]],
                )


if __name__ == "__main__":
    main()
