from brands.apricotstudios.client import ApricotStudiosClient


def apricot_26spring_babycot_end_discount(testrun=True):
    client = ApricotStudiosClient()
    products = client.products_by_collection_id("474890764544")
    client.revert_product_prices(products, testrun=testrun)


def start_end_discounts_season_off_sale(testrun=True, start_or_end="end"):
    """
    Apricot Studios 26 Autumn & Winter Season Off Event
    """
    client = ApricotStudiosClient()

    tag_rate_map = {
        "2026_season_off_sale_30%": 0.7,
        "2026_season_off_sale_20%": 0.8,
        "2026_season_off_sale_15%": 0.85,
        "2026_season_off_sale_10%": 0.9,
    }

    for tag, rate in tag_rate_map.items():
        products = client.products_by_tag(tag)
        if not products:
            print(f"No products found for tag: {tag}")
            continue

        if start_or_end == "end":
            client.revert_product_prices(products, testrun=testrun)
        else:
            new_prices_by_variant_id = {
                v["id"]: int(int(v["compareAtPrice"] or v["price"]) * rate)
                for p in products
                for v in p["variants"]["nodes"]
            }
            client.update_product_prices_by_dict(
                products,
                new_prices_by_variant_id=new_prices_by_variant_id,
                testrun=testrun,
            )


def main():
    pass


if __name__ == "__main__":
    main()
