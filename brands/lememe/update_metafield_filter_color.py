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
from brands.lememe.product_create import product_info_list_from_sheet

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("lememek")
    product_info_list = product_info_list_from_sheet(
        client, client.sheet_id, "bags - launch"
    )
    for product_info in product_info_list:
        for option in product_info["options"]:
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
