import datetime
import pprint
from brands.lememe.client import LememeClientApparel


def get_date_metafield_value(metafields, key):
    if metafield := [m for m in metafields if m["key"] == key]:
        return datetime.datetime.fromisoformat(metafield[0]["value"]).date()


def main():
    client = LememeClientApparel(product_sheet_start_row=1)
    product_inputs = client.product_inputs_by_sheet_name(sheet_name="0305_RTW_spring")

    products_with_value = []
    variants_with_value = []

    for p in product_inputs:
        product_title = p["title"]
        products = client.products_by_query(
            f"title:{product_title}* AND status:'ARCHIVED'"
        )

        for product in products:
            if expected_shipping_date := get_date_metafield_value(
                product["metafields"]["nodes"], "expected_shipping_date"
            ):
                if expected_shipping_date:
                    products_with_value.append(
                        (expected_shipping_date, product["title"])
                    )

            for variant in product["variants"]["nodes"]:
                if variant_expected_shipping_date := get_date_metafield_value(
                    variant["metafields"]["nodes"], "variant_expected_shipping_date"
                ):
                    if variant_expected_shipping_date:
                        variants_with_value.append(
                            (
                                variant_expected_shipping_date,
                                variant["displayName"],
                            )
                        )

    print("products_with_value:")
    pprint.pprint(products_with_value)

    print("\nvariants_with_value:")
    pprint.pprint(variants_with_value)


if __name__ == "__main__":
    main()
