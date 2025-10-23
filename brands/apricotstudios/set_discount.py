import utils


def main():
    client = utils.client("apricot-studios")
    products = client.products_by_metafield("custom", "discount_rate", "15%")
    for p in products:
        for variant in p["variants"]["nodes"]:
            if not variant["compareAtPrice"] or (
                variant["compareAtPrice"] == variant["price"]
            ):
                compare_at_price = variant["compareAtPrice"] or variant["price"]
                price = int(int(compare_at_price) * 0.85)
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
