import pandas as pd
import utils

skus_to_ignore_stdev = [
    "JLL00CC4NBK",  # mini-root-backpack-Nylon
    "JLL00CC4NMU",
    "JLL00CC4NSM",
    "JLL00CC4NGR",
    "JLL00CC3NBE",  # root-backpack-Nylon-1
]


def main():
    client = utils.client("rohseoul")
    df = pd.read_csv(
        "/Users/taro/Downloads/ROH SEOUL Japan EC Product Details - 20250917_discontinued.csv"
    )
    grouped = (
        df.groupby("Handle", sort=False)["SKU"].apply(list).reset_index(name="SKU_List")
    )
    skus_by_handle = grouped.set_index("Handle")["SKU_List"].to_dict()
    for handle, skus in skus_by_handle.items():
        if not any(sku in skus_to_ignore_stdev for sku in skus):
            try:
                variant_id = client.variant_id_by_sku(skus[0], active_only=False)
                client.medias_by_variant_id(variant_id)
            except AssertionError as e:
                print(f"check media: {handle} {skus}: {e}")


if __name__ == "__main__":
    main()
