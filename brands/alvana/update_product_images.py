import logging

logging.basicConfig(level=logging.INFO)


def main():
    titles = ["SUMMER WOOL FR TEE SHIRTS", "SUMMER WOOL L/S TEE SHIRTS"]
    from utils import client
    import pprint

    c = client("alvanas")
    product_inputs = c.product_inputs_by_sheet_name("Product Master")
    ress = []
    for product_input in product_inputs:
        if product_input["title"] in titles:
            print(f'processing {product_input["title"]}')
            ress.append(c.process_product_images(product_input))
    pprint.pprint(ress)


if __name__ == "__main__":
    main()
