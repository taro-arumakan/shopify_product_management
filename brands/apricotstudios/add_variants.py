import logging

from brands.apricotstudios.client import ApricotStudiosClient

logging.basicConfig(level=logging.INFO)


def main():
    sheet_name = "[NEW] 9/10 Castanets Backpack"
    client = ApricotStudiosClient(product_sheet_start_row=1)
    product_inputs = client.product_inputs_by_sheet_name(sheet_name)

    res = client.check_existing_skus(product_inputs)
    if res:
        for r in res:
            logging.error(r)
        raise RuntimeError("Existing SKUs found; aborting add_variants")

    for product_input in product_inputs:
        logging.info(f"adding variants for {product_input['title']}")
        client.add_variants_from_product_input(product_input)


if __name__ == "__main__":
    main()
