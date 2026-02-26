import logging

logging.basicConfig(level=logging.INFO)

from brands.blossom.client import BlossomClientClothes


def main():
    sheet_name = "0225soffi"
    client = BlossomClientClothes(product_sheet_start_row=0)
    product_inputs = client.product_inputs_by_sheet_name(sheet_name)
    for product_input in product_inputs:
        client.add_variants_from_product_input(product_input)

    for product_input in product_inputs:
        product = client.product_by_title(product_input["title"])
        new_variant_prices_by_variant_id = {
            v["id"]: int(int(v["compareAtPrice"]) * 0.8)
            for v in product["variants"]["nodes"]
        }
        client.update_product_prices_by_dict(
            [product],
            new_prices_by_variant_id=new_variant_prices_by_variant_id,
            testrun=False,
        )


if __name__ == "__main__":
    main()
