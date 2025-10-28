import logging
from brands.ssil.client import SsilClient, SsilClientMaterialOptionOnly

logging.basicConfig(level=logging.INFO)


def main():
    reprocess_products = [
        "OVAL PEARL COLLAR_L",
        "OVAL PEARL COLLAR_S",
        "3 LINE HOOPS_L_C",
        "3 LINE HOOPS_L",
        "3 LINE HOOPS_S_C",
        "3 LINE HOOPS_S",
        "CLOVER BALL PEARL COLLAR",
        "SILVER ROPE CHOKER",
    ]
    clients = [SsilClient(), SsilClientMaterialOptionOnly()]
    sheet_names = ["material & size options (rings etc)", "material options only"]
    restart_at_product_names = [None, None]
    # for client, sheet_name in zip(clients, sheet_names):
    #     client.sanity_check_sheet(sheet_name)

    for client, sheet_name, restart_at_product_name in zip(
        clients, sheet_names, restart_at_product_names
    ):
        product_info_list = client.product_info_list_from_sheet(sheet_name)
        product_info_list = [
            pi for pi in product_info_list if pi["title"] in reprocess_products
        ]
        for pi in product_info_list:
            client.create_product_from_product_info(pi)
            client.process_product_images(pi)
        client.update_stocks(product_info_list)
        client.publish_products(product_info_list)


if __name__ == "__main__":
    main()
