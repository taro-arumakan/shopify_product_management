import logging
import pprint
import string
import numpy as np
import pandas as pd

from brands.alvana.client import AlvanaClient

SHOPNAME = "alvanas"
SHEET_TITLE = "Product Master"

start_row = 1
column_map = {
    "sku": string.ascii_uppercase.index("M"),
    "quantity": string.ascii_uppercase.index("N"),
}


def option_value(selected_options, name):
    for o in selected_options:
        if o["name"] == name:
            return o["value"]


variants_by_product_sku = {}


def sku_by_product_sku_and_selected_options(
    client: AlvanaClient, product_sku, color, size
):
    if product_sku not in variants_by_product_sku:
        logging.info(f"querying variants for {product_sku}")
        variants_by_product_sku[product_sku] = client.product_variants_by_query(
            f"sku:{product_sku}*"
        )
    variants = variants_by_product_sku[product_sku]
    for v in variants:
        if (
            v["sku"].startswith(product_sku)
            and option_value(v["selectedOptions"], "カラー") == color
            and option_value(v["selectedOptions"], "サイズ") == str(size)
        ):
            return v["sku"]


from functools import lru_cache


@lru_cache(maxsize=128)
def cached_sku_lookup(client: AlvanaClient, product_sku, color, size):
    return sku_by_product_sku_and_selected_options(client, product_sku, color, size)


def df_with_sku_from_sheet(client: AlvanaClient, sheet_title):
    rows = client.worksheet_rows(
        "1B30K6DCHtjTP3H4s9I8BX4zfZvTgkZ77SM0EFSUhqA0", sheet_title
    )
    df = pd.DataFrame(rows[3:], columns=rows[2])
    cols_to_fix = ["品番", "色"]

    for col in cols_to_fix:
        df[col] = df[col].replace(r"^\s*$", np.nan, regex=True)
    df.loc[df["品番"].astype(str).str.startswith("（", na=False), "品番"] = np.nan

    df[cols_to_fix] = df[cols_to_fix].ffill()

    product_sku_map = {
        "ALV-90114-A": "ALV-90114",
        "ALV-90112-A 25SS（新）": "ALV-90112",
        "ALV-90107-A": "ALV-90107",
    }
    df["variant_sku"] = df.apply(
        lambda row: cached_sku_lookup(
            client,
            product_sku_map.get(row["品番"], row["品番"]),
            row["色"],
            row["SIZE"],
        ),
        axis=1,
    )
    return df


def update_stocks(client: AlvanaClient, sku_quantity_map):
    location_id = client.location_id_by_name(client.LOCATIONS[0])
    assert location_id, "location id not found"

    for sku, quantity in sku_quantity_map.items():
        res = client.set_inventory_quantity_by_sku_and_location_id(
            sku, location_id, quantity
        )
        logging.info(f"updated {sku} to {quantity}: {res}")


def main():
    logging.basicConfig(level=logging.INFO)
    sheet_titles = [
        "在庫表（布帛デニム）2025年9月25日～",
        # "在庫表（カットニット）2025年9月25日～"
    ]
    client = AlvanaClient()
    for sheet_title in sheet_titles:
        df = df_with_sku_from_sheet(client, sheet_title)
        for v in df["variant_sku"]:
            print(v if type(v) == str else "")
        sku_quantity_map = (
            df[df["variant_sku"].notna()]
            .groupby("variant_sku")["現在個"]
            .sum()
            .to_dict()
        )
        pprint.pprint(sku_quantity_map)
        # update_stocks(client, sku_quantity_map)


if __name__ == "__main__":
    main()
