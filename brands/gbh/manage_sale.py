from brands.gbh.client import GbhClient
import utils
import pandas as pd


def start_end_discounts(testrun=True, start_or_end="end"):
    client = GbhClient()
    products = client.products_by_query("tag:'HOME'")

    if start_or_end == "end":
        client.revert_product_prices(products, testrun=testrun)
    else:
        new_prices_by_variant_id = {
            v["id"]: int(int(v["compareAtPrice"] or v["price"]) * 0.9)
            for p in products
            for v in p["variants"]["nodes"]
        }
        client.update_product_prices_by_dict(
            products, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
        )


if __name__ == "__main__":
    start_end_discounts()
