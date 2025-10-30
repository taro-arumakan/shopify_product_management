import utils


def main():
    client = utils.client("apricot-studios")
    products = client.products_by_query(
        'metafields.custom.discount_rate:"15%" AND status:ACTIVE'
    )
    for p in products:
        for variant in p["variants"]["nodes"]:
            price = int(variant["price"])
            compare_at_price = int(variant["compareAtPrice"])
            assert compare_at_price
            print(
                f"Updating price of {p['title']} - {variant['selectedOptions']} from {price} to {compare_at_price}"
            )
            client.update_variant_attributes(
                product_id=p["id"],
                variant_id=variant["id"],
                attribute_names=["price"],
                attribute_values=[str(compare_at_price)],
            )


if __name__ == "__main__":
    main()
