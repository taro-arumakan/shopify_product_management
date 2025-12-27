from brands.kume.client import KumeClient


def end_final_sale(testrun=True):
    client = KumeClient()
    products = client.products_by_tag("FINAL SALE")
    client.revert_product_prices(products, testrun=testrun)


if __name__ == "__main__":
    end_final_sale()

