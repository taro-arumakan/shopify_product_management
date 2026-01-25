import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("gbhjapan")
    product_inputs = client.product_inputs_by_sheet_name("APPAREL 25FW (WINTER 1次)")
    product_input = product_inputs[0]
    client.add_variants_from_product_input(product_input)


if __name__ == "__main__":
    main()
