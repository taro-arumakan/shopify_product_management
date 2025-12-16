import utils


def main():
    client = utils.client("blossomhcompany")
    products = client.products_by_query("tag_not:'25_drop7' AND status:'ACTIVE'")
    print(len(products))
    for p in products:
        for variant in p["variants"]["nodes"]:
            if variant["price"] != variant["compareAtPrice"]:
                client.update_variant_prices_by_variant_ids(
                    product_id=p["id"],
                    variant_ids=[variant["id"]],
                    prices=[variant["compareAtPrice"]],
                    compare_at_prices=[variant["compareAtPrice"]],
                )


if __name__ == "__main__":
    main()
