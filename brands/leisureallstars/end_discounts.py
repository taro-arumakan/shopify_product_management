import utils


def main():
    client = utils.client("leisureallstars")
    products = client.products_by_query("status:'ACTIVE'")
    products = [
        p for p in products if all(v["compareAtPrice"] for v in p["variants"]["nodes"])
    ]
    client.revert_product_prices(products=products, testrun=False)


if __name__ == "__main__":
    main()
