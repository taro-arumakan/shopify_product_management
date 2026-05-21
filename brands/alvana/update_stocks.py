import logging

logging.basicConfig(level=logging.INFO)

from brands.alvana.client import AlvanaClient


def main():
    sheet_name = "26SS Product Master"
    client = AlvanaClient(product_sheet_start_row=1)
    product_inputs = client.product_inputs_by_sheet_name(sheet_name)
    location_id = client.location_id_by_name(client.LOCATIONS[0])
    for product_input in product_inputs:
        for color_option in product_input["options"]:
            for size_option in color_option["options"]:
                if stock := size_option["stock"]:
                    if color_option["drive_link"] == "no image":
                        pass
                    else:
                        sku = size_option["sku"]
                        variant = client.variant_by_sku(sku)
                        print(
                            f"{variant['sku']}: update stock from {variant['inventoryQuantity']} to {stock}: {variant['displayName']}"
                        )
                        client.set_inventory_quantity_by_sku_and_location_id(
                            sku, location_id, stock
                        )


if __name__ == "__main__":
    main()
