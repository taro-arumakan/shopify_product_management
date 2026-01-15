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

    variants = [client.variant_by_sku(sku) for sku in skus]

    if start_or_end == "end":
        client.revert_variant_prices(variants, testrun=testrun)
    else:
        new_prices_by_variant_id = {
            v["id"]: int(int(v["compareAtPrice"] or v["price"]) * 0.85)
            for v in variants
        }
        client.update_variant_prices_by_dict(
            variants, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
        )


if __name__ == "__main__":
    start_end_discounts()
