import logging
from brands.ssil.client import SsilClient

logging.basicConfig(level=logging.INFO)


def main():
    client = SsilClient(product_sheet_start_row=1)
    product_inputs = client.product_inputs_by_sheet_name("NEW CLOVER")
    product_input = product_inputs[3]
    client.add_variants_from_product_input(product_input)


if __name__ == "__main__":
    main()
