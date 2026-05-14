import pandas as pd
import utils

skus = [
    "JLL00CC6SBK",
    "JLL00CC6UCN",
    "JLL00CC7SBK",
    "JLL00CC7UCN",
    "JLL00CG8SBK",
    "JLL00CG8UCN",
    "JLL00CG4SBK",
]


def main():
    client = utils.client("rohseoul")
    for sku in skus:
        try:
            variant_id = client.variant_id_by_sku(skus[0], active_only=False)
            client.medias_by_variant_id(variant_id)
        except AssertionError as e:
            print(f"check media: {sku}: {e}")


if __name__ == "__main__":
    main()
