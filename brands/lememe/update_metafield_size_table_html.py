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
        size_table_html = client.get_size_field(pi)
        print(f"updating size_table_html {product['title']}:")
        print(
            f"before:\n{[m for m in product["metafields"]["nodes"] if m["key"] == "size_table_html"][0]["value"]}"
        )
        print(f"after:\n{size_table_html}")
        print()

        client.update_size_table_html_metafield(product["id"], size_table_html)


if __name__ == "__main__":
    main()
