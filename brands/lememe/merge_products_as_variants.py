import logging
from brands.lememe.client import LememeClientApparel


logging.basicConfig(level=logging.INFO)


def main():
    client = LememeClientApparel(product_sheet_start_row=1)
    product_inputs = client.product_inputs_by_sheet_name(sheet_name="0305_RTW_spring")
    for p in product_inputs:
        product_title = p["title"]
        products = client.products_by_query(f"title:{product_title}*")
        if len(products) == 1:
            client.update_product_attribute(products[0]["id"], "title", product_title)
        else:
            client.merge_products_as_variants(
                products=products, new_product_title=product_title
            )


if __name__ == "__main__":
    main()
