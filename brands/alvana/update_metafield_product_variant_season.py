import logging
import helpers.exceptions
from brands.alvana.client import AlvanaClient

logging.basicConfig(level=logging.INFO)


def process(sheet_name):
    client = AlvanaClient(product_sheet_start_row=1)
    product_inputs = client.product_inputs_by_sheet_name(sheet_name)

    for product_input in product_inputs:
        for color_option in product_input["options"]:
            for size_option in color_option["options"]:
                variant = client.variant_by_sku(size_option["sku"])
                variant_id = variant["id"]
                product_id = variant["product"]["id"]
                client.update_variant_metafield(
                    product_id, variant_id, "custom", "product_variant_season", "26ss"
                )


def main():
    for sheet_name in ["26SS Product Master", "26SS Product Master 変更"]:
        process(sheet_name)


if __name__ == "__main__":
    main()
