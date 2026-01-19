from brands.blossom.client import BlossomClient
import utils
import pandas as pd

# Blossom 1/23 - 2/1 outer sale 30% off
def start_end_discounts(testrun=True, start_or_end="start"):
    client = BlossomClient()
    products = client.products_by_query("tag:'OUTER' AND tag_not:'drop11' AND tag_not:'drop12'")

    if start_or_end == "end":
        client.revert_product_prices(products, testrun=testrun)
    else:
        new_prices_by_variant_id = {
            v["id"]: int(int(v["compareAtPrice"] or v["price"]) * 0.7)
            for p in products
            for v in p["variants"]["nodes"]
        }
        client.update_product_prices_by_dict(
            products, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
        )


def main():
    start_end_discounts()
    # start_end_discounts(testrun=False, start_or_end="end")


if __name__ == "__main__":
    main()
