import logging
from brands.ssil.client import SsilClient, SsilClientMaterialOptionOnly

logging.basicConfig(level=logging.INFO)


def main():
    client = SsilClient()
    sheet_name = "material & size options (rings etc)"
    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(
        sheet_name,
        restart_at_product_name="X LOCK OVAL PEARL N",
        additinal_tags=["New Arrival"],
    )

    client = SsilClientMaterialOptionOnly()
    sheet_name = "material options only"
    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(sheet_name, additinal_tags=["New Arrival"])


if __name__ == "__main__":
    main()
