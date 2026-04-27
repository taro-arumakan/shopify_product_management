import logging

logging.basicConfig(level=logging.INFO)

import datetime
import os
from brands.blossom.client import BlossomClientClothes
from brands.dev.client import dev_client


def main():

    client = dev_client(
        BlossomClientClothes(
            remove_existing_new_product_indicators=False, product_sheet_start_row=1
        )
    )

    sheet_names = ["clothes(drop5)", "clothes(drop6)"]
    drop_tags = ["drop5", "drop6"]

    for sheet_name, drop_tag in zip(sheet_names, drop_tags):
        client.products_season_tag = drop_tag
        try:
            client.sanity_check_sheet(sheet_name)
        except RuntimeError as e:
            logging.error(f"Sanity check failed for {sheet_name}: {e}")

    for sheet_name, drop_tag in zip(sheet_names, drop_tags):
        client.products_season_tag = drop_tag
        client.process_sheet_to_products(sheet_name=sheet_name)


if __name__ == "__main__":
    main()
