import logging
from brands.ssil.client import SsilClient, SsilClientMaterialOptionOnly

logging.basicConfig(level=logging.INFO)


def main():

    clients = [SsilClient(), SsilClientMaterialOptionOnly()]
    sheet_names = ["material & size options (rings etc)", "material options only"]
    restart_at_product_names = ["DO NOT CREATE", None]
    for client, sheet_name in zip(clients, sheet_names):
        client.sanity_check_sheet(sheet_name)

    for client, sheet_name, restart_at_product_name in zip(
        clients, sheet_names, restart_at_product_names
    ):
        client.process_sheet_to_products(
            sheet_name, restart_at_product_name=restart_at_product_name
        )


if __name__ == "__main__":
    main()
