from brands.archivepke.client import ArchivepkeClient


def start_end_discounts(testrun=True, start_or_end="end"):
    client = ArchivepkeClient()

    # New Year Appreciation Promotion
    skus = [
        "OVBAX25004BLK",
        "OVBAX25005BLK",
        "OVBAX25229DKB",
        "OVBAX26004SBK",
        "OVBAX26004SCR",
        "OVBAX25115BLK",
        "OVBRX25102BLK",
    ]

    product_ids = {client.product_id_by_sku(sku) for sku in skus}
    products = [client.product_by_id(pid) for pid in product_ids]

    if start_or_end == "end":
        client.revert_product_prices(products, testrun=testrun)
    else:
        new_prices_by_variant_id = {
            v["id"]: int(int(v["compareAtPrice"] or v["price"]) * 0.85)
            for p in products
            for v in p["variants"]["nodes"]
            if v["sku"] in skus
        }
        client.update_product_prices_by_dict(
            products, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
        )


if __name__ == "__main__":
    start_end_discounts()
