color_code_map = {
    "Black": "#000000",
    "Brown": "#8B4513",
    "Red": "#FF0000",
    "Ivory": "#FFFFF0",
    "Cream": "#FFFDD0",
    "Beige": "#F5F5DC",
}

import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("lememek")
    product_inputs = client.product_inputs_by_sheet_name("bags - launch")

    for product_input in product_inputs:
        for option in product_input["options"]:
            sku = option["sku"]
            filter_color = option["filter_color"]
            variant = client.variant_by_sku(sku)
            variant_id = variant["id"]
            product_id = variant["product"]["id"]
            client.update_variant_metafield(
                product_id, variant_id, "custom", "filter_color", filter_color
            )


if __name__ == "__main__":
    main()
