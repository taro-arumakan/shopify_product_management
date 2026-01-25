import logging
import helpers.exceptions
from brands.alvana.client import AlvanaClient

logging.basicConfig(level=logging.INFO)


def main():
    client = AlvanaClient()
    product_inputs = client.product_inputs_by_sheet_name("Product Master")
    for product_input in product_inputs:
        for option in product_input["options"]:
            filter_color = option["filter_color"]
            for o2 in option["options"]:
                sku = o2["sku"]
                try:
                    variant = client.variant_by_sku(sku)
                    variant_id = variant["id"]
                    product_id = variant["product"]["id"]
                    client.update_variant_metafield(
                        product_id, variant_id, "custom", "filter_color", filter_color
                    )
                except helpers.exceptions.NoVariantsFoundException as e:
                    print(f"{product_input['title']}: {sku}")

    products = client.products_by_query("status:'ACTIVE'")
    for product in products:
        for variant in product["variants"]["nodes"]:
            filter_color_field = [
                m for m in variant["metafields"]["nodes"] if m["key"] == "filter_color"
            ]
            if not filter_color_field:
                print(f"missing filter color: {product['title']}")
            else:
                filter_color = filter_color_field[0]["value"]
                if filter_color in ["GLAY", "INK BLACK", "SEAWEED"]:
                    print(f"{product['title']}: {filter_color}")


if __name__ == "__main__":
    main()
