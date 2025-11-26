import pandas as pd
import utils


def main():
    client = utils.client("leisureallstars")
    products = client.products_by_query("vendor:'ATLAS'")
    for product in products:
        for variant in product["variants"]["nodes"]:
            original_price = int(variant["compareAtPrice"] or variant["price"])
            discount_price = int(original_price * 0.5)
            print(
                f"going to update price of {variant['displayName']} from {original_price} to {discount_price}"
            )
            client.update_variant_price_by_variant_id(
                product_id=product["id"],
                variant_ids=[variant["id"]],
                prices=[discount_price],
                compare_at_prices=[original_price],
            )


if __name__ == "__main__":
    main()
