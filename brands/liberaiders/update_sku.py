import logging
import utils
from brands.liberaiders.product_create import product_info_list_from_sheet


logging.basicConfig(level=logging.INFO)


def get_variant(client: utils.Client, barcode: str, sku: str):
    try:
        return client.variant_by_sku(barcode)
    except utils.NoVariantsFoundException as ex:
        return client.variant_by_sku(sku)


def main():
    c = utils.client("liberaiders")
    product_info_list = product_info_list_from_sheet(c, c.sheet_id, "Product Master")
    for i, pi in enumerate(product_info_list):
        if pi["title"] == "CIRCLE LOGO CREWNECK":
            break
    for product_info in product_info_list[i:]:
        for color_option in product_info["options"]:
            for size_option in color_option["options"]:
                sku = size_option["sku"]
                barcode = size_option["barcode"]
                variant = get_variant(c, barcode, sku)
                product_id = variant["product"]["id"]
                c.update_a_variant_attributes(
                    product_id, variant["id"], ["barcode"], [barcode], sku=sku
                )


if __name__ == "__main__":
    main()
