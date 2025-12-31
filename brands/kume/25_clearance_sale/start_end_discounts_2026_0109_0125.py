from brands.kume.client import KumeClient


def start_end_discounts_2026_0109_0125(testrun=True, start_or_end="end"):
    client = KumeClient()
    tag_rate_map = {"2025_fs_30%": 0.7, "2025_fs_20%": 0.8, "2025_fs_15%": 0.85}

    for tag, rate in tag_rate_map.items():
        products = client.products_by_tag(tag)
        if not products:
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


if __name__ == "__main__":
    start_end_discounts_2026_0109_0125()
