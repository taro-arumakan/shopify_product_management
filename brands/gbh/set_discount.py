import utils


def main():
    client = utils.client("gbhjapan")
    products = client.products_by_tag("COSMETICS", raise_if_too_many=False)
    for p in products:
        for variant in p["variants"]["nodes"]:
            compare_at_price = variant["compareAtPrice"] or variant["price"]
            price = round(int(compare_at_price) * 0.7)
            print(
                f"Updating price of {p['title']} - {variant['selectedOptions']} from {compare_at_price} to {price}"
            )
            client.update_variant_attributes(
                product_id=p["id"],
                variant_id=variant["id"],
                attribute_names=["price", "compareAtPrice"],
                attribute_values=[str(price), str(compare_at_price)],
            )


if __name__ == "__main__":
    main()
