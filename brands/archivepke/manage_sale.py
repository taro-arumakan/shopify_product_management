from brands.archivepke.client import ArchivepkeClient


def start_end_discounts(testrun=True, start_or_end="end"):
    client = ArchivepkeClient()

    # 26SS NEW COLOR 15% PROMOTION 3.5~3.15
    skus = [
    "OVBAX26051GBK",
    "OVBAX26051GGR",
    "OVBAX26052GBK",
    "OVBAX26052SCR",
    "OVBAX26053BLK",
    "OVBAX26053IGR",
    "OVBAX26055BLK",
    "OVBAX26055CMI",
    "OVBAX26055OBG",
    "OVBSX26055BLK",
    "OVBSX26154BLK"
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
