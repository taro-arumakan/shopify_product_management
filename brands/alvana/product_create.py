import logging
from brands.alvana.client import AlvanaClient

logging.basicConfig(level=logging.INFO)


def main():

    client = AlvanaClient(
        product_sheet_start_row=1,
        products_season_tag="26ss",
        remove_existing_new_product_indicators=True,
    )
    client.sanity_check_sheet("26SS Product Master")
    client.process_sheet_to_products("26SS Product Master")


if __name__ == "__main__":
    main()
