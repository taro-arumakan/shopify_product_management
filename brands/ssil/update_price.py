from brands.ssil.client import SsilClientGoldLine


def update_price():
    client = SsilClientGoldLine(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag="debug_gold",
    )
    product_inputs = client.product_inputs_by_sheet_name("GOLD PRODUCT")
    # client.sanity_check_product_inputs(product_inputs)
    skus = [
        so["sku"]
        for pi in product_inputs
        for co in pi["options"]
        for so in co["options"]
    ]
    variants = client.variants_by_skus(skus)
    new_prices_by_variant_id = {}
    for pi in product_inputs:
        for color_option in pi["options"]:
            for size_option in color_option["options"]:
                variant = [v for v in variants if v["sku"] == size_option["sku"]]
                assert len(variant) == 1
                variant = variant[0]
                print(
                    f"updating {size_option['sku']} from {variant['price']} to {size_option['price']}"
                )
                new_prices_by_variant_id[variant["id"]] = size_option["price"]
    client.update_variant_prices_by_dict(variants, new_prices_by_variant_id, False)


if __name__ == "__main__":
    update_price()
