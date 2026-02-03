from brands.blossom.client import BlossomClient
import utils
import pandas as pd

# Blossom 2/7 - END OF SEASON SALE ALL 20% OFF
def start_end_discounts(testrun=True, start_or_end="start"):
    client = BlossomClient()
    products = client.products_by_query("tag_not:'BAG' AND tag_not:'ACC' AND tag_not:'SHOES'")

    if start_or_end == "end":
        client.revert_product_prices(products, testrun=testrun)
    else:
        new_prices_by_variant_id = {
            v["id"]: int(int(v["compareAtPrice"] or v["price"]) * 0.8)
            for p in products
            for v in p["variants"]["nodes"]
        }
        client.update_product_prices_by_dict(
            products, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
        )


def main():
    start_end_discounts()


if __name__ == "__main__":
    main()
