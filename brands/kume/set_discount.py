import utils


def main():
    client = utils.client("kumej")
    products = client.products_by_tag("25SS-HOTSUMMER")
    for p in products:
        for variant in p["variants"]["nodes"]:
            compare_at_price = variant["compareAtPrice"] or variant["price"]
            price = int(int(compare_at_price) * 0.9)
            print(
                f"Updating price of {variant['id']} from {compare_at_price} to {price}"
            )
            client.update_a_variant_attributes(
                product_id=p["id"],
                variant_id=variant["id"],
                attribute_names=["price", "compareAtPrice"],
                attribute_values=[str(price), str(compare_at_price)],
            )


if __name__ == "__main__":
    main()
