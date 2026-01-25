import logging

logging.basicConfig(level=logging.INFO)


def main():
    from utils import client
    import pprint

    c = client("kumej")
    titles = """Tweed Short Sleeve Blouse
Ribbon Boxer Shorts
Linen Pleated Long Skirt
H-line Knitted Skirt
Twisted Back Detail T-shirt""".split(
        "\n"
    )

    product_inputs = c.product_inputs_by_sheet_name("25ss")
    product_inputs = [
        product_input
        for product_input in product_inputs
        if product_input["title"] in titles
    ]
    assert len(titles) == len(product_inputs)
    ress = []
    for product_input in product_inputs:
        print(f'processing {product_input["title"]}')
        c.process_product_images(product_input)
    pprint.pprint(ress)


if __name__ == "__main__":
    main()
