import utils


def main():
    client = utils.client("apricot")

    pil = client.product_inputs_by_sheet_name("11.20 25Winter_clone")

    for pi in pil:
        product = client.product_by_title(pi["title"])
        compare_at_prices, prices, skus = [], [], []
        for o1 in pi["options"]:
            for o2 in o1["options"]:
                compare_at_price = o2["price"]
                compare_at_prices.append(compare_at_price)
                prices.append(int(int(compare_at_price) * 0.9))
                skus.append(o2["sku"])
        client.update_variant_prices_by_skus(
            product["id"], skus=skus, prices=prices, compare_at_prices=compare_at_prices
        )


if __name__ == "__main__":
    main()
