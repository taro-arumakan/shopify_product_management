import logging
from brands.lememe.client import LememeClientApparel


logging.basicConfig(level=logging.INFO)


def main():
    client = LememeClientApparel(
        product_sheet_start_row=1,
    )
    sheet_name = "0520_RTW_summer"

    product_inputs = client.product_inputs_by_sheet_name(sheet_name)
    for pi in product_inputs:
        product = client.product_by_title(pi["title"])
        description = client.get_description_html(pi)
        print(f"updating description {product['title']}:")
        print(description)
        print()

        client.update_product_description(product["id"], description)


if __name__ == "__main__":
    main()
