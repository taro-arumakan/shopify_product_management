import logging
import string
import utils

logging.basicConfig(level=logging.INFO)

sheet_id = "1SzaDFzw513CA-vaGeAoRyd6N9eA_IwOg_JjdYSsSa9g"


def main():
    client = utils.client("gbhjapan")
    rows = client.worksheet_rows(sheet_id, "시트1")

    for row in rows[2:]:
        sku = row[string.ascii_uppercase.index("F")]
        price = int(row[string.ascii_uppercase.index("I")])
        try:
            variant = client.variant_by_sku(sku)
            print(
                f"Updating price of {variant['product']['title']} - {variant['title']} from {variant['price']} to {price}"
            )
            client.update_variant_attributes(
                product_id=variant["product"]["id"],
                variant_id=variant["id"],
                attribute_names=["price", "compareAtPrice"],
                attribute_values=[str(price), str(price)],
            )
        except utils.NoVariantsFoundException:
            print(f"SKU not found: {row[string.ascii_uppercase.index('C')]}: {sku}")
            continue


if __name__ == "__main__":
    main()
