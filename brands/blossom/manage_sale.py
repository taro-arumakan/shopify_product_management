from brands.blossom.client import BlossomClient
import utils
import pandas as pd


# Blossom 26SS drop3 10% OFF
def start_end_discounts(testrun=True, start_or_end="start"):
    client = BlossomClient()

    skus = [
        "BC2601SPPT005-01-GR-XS",
        "BC2601SPPT005-01-GR-S",
        "BC2601SPPT005-01-GR-M",
        "BC2602SPBL004-01-GR-S",
        "BC2602SPBL004-01-GR-M",
        "BC2601SPSK001-01-GR-XS",
        "BC2601SPSK001-01-GR-S",
        "BC2601SPSK001-01-GR-M",
        "BC2601SPBL002-01-IV-S",
        "BC2601SPBL002-01-IV-M",
        "BC2601SPBL002-01-GR-S",
        "BC2601SPBL002-01-GR-M",
        "BC2601SPBL002-01-KB-S",
        "BC2601SPBL002-01-KB-M",
        "BC2601SPBL002-01-BK-S",
        "BC2601SPBL002-01-BK-M",
        "BC2601SPCT001-01-GR-S",
        "BC2601SPCT001-01-GR-M",
        "BC2601SPCT001-01-KB-S",
        "BC2601SPCT001-01-KB-M",
        "BC2601SPCT001-01-BK-S",
        "BC2601SPCT001-01-BK-M",
    ]

    variants = [client.variant_by_sku(sku) for sku in skus]

    if start_or_end == "end":
        client.revert_variant_prices(variants, testrun=testrun)
    else:
        new_prices_by_variant_id = {
            v["id"]: int(int(v["compareAtPrice"] or v["price"]) * 0.9) for v in variants
        }
        client.update_variant_prices_by_dict(
            variants, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
        )


def main():
    start_end_discounts()


if __name__ == "__main__":
    main()
