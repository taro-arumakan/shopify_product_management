from brands.kume.client import KumeClient


def start_end_discounts_spring_sale(testrun=True, start_or_end="start"):
    """
    KUME 2/6-2/15 Spring Sale
    """
    client = KumeClient()
    
    tag_rate_map = {
        "2026_SpringSale_40%": 0.6,
        "2026_SpringSale_30%": 0.7,
        "2026_SpringSale_20%": 0.8,
        "2026_SpringSale_15%": 0.85,
        "2026_SpringSale_10%": 0.9,
    }

    for tag, rate in tag_rate_map.items():
        products = client.products_by_tag(tag)

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
    start_end_discounts_spring_sale(testrun=True, start_or_end="start")

if __name__ == "__main__":
    main()
