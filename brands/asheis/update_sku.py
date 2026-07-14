import logging
from brands.asheis.client import AsheisClient


def variant_by_option_values(product, option_values):
    selected_options = [dict(name=k, value=v) for k, v in option_values.items()]
    for variant in product["variants"]["nodes"]:
        if variant["selectedOptions"] == selected_options:
            return variant


def main():
    logging.basicConfig(level=logging.DEBUG)
    client = AsheisClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
    )
    product_inputs = client.product_inputs_by_sheet_name("【8_9デリ】Products Master")
    for pi in product_inputs:
        product = client.product_by_title(pi["title"])
        print(product["id"], product["title"])
        options = client.populate_option_dicts(pi)
        variants = [
            variant_by_option_values(product, option["option_values"])
            for option in options
        ]
        skus = [option["sku"] for option in options]
        print([v["id"] for v in variants], [v["sku"] for v in variants], "to", skus)
        client.update_variant_sku_by_variant_id(
            product["id"], [v["id"] for v in variants], skus
        )


if __name__ == "__main__":
    main()
