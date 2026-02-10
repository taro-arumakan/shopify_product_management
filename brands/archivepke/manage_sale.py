from brands.archivepke.client import ArchivepkeClient


def start_end_discounts(testrun=True, start_or_end="end"):
    client = ArchivepkeClient()

    # 26SS NEW COLOR PROMOTION 2.21~2.28 ALL 15% OFF
    skus = [
        "OVBAX26001CMI",
        "OVBAX26001GGR",
        "OVBAX26001GMB",
        "OVBAX26001GOB",
        "OVBAX26001HRD",
        "OVBAX26001OBG",
        "OVBAX26002IGR",
        "OVBAX26002MBR",
        "OVBAX26002OBG",
        "OVBAX26004GGR",
        "OVBAX26004MBR",
        "OVBAX26004OBG",
        "OVBAX26105IVO",
        "OVBAX26107BRW",
        "OVBAX26107WBL",
        "OVBAX26108DKB",
        "OVBAX26108DPK",
        "OVBAX26108WHT",
        "OVBAX26104BRW",
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
