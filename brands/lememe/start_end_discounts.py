import utils


def start_end_discounts_2025_new_year(testrun=True, start_or_end="end"):
    client = utils.client("lememe")
    products = client.products_by_query()

    if start_or_end == "end":
        client.revert_product_prices(products, testrun=testrun)
    else:
        new_prices_by_variant_id = {
            v["id"]: int(int(v["compareAtPrice"] or v["price"]) * 0.95)
            for p in products
            for v in p["variants"]["nodes"]
        }
        client.update_product_prices_by_dict(
            products, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
        )
