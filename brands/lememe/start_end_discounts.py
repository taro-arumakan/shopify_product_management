import utils

EXCLUDED_TITLES = {
    "Clelf Necklace",
    "Frame Petit Lip Poche",
    "Noah Dress White",
}


def start_end_discounts_26_summer_sale(testrun=True, start_or_end="start"):
    """26 SUMMER SALE: 全商品5%OFF（対象外3商品を除く）"""
    client = utils.client("lememe")
    products = [
        p
        for p in client.products_by_query()
        if p["title"] not in EXCLUDED_TITLES
    ]

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


def main():
    start_end_discounts_26_summer_sale(testrun=True, start_or_end="start")


if __name__ == "__main__":
    main()
