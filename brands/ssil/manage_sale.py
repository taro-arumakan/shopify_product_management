import utils
import pandas as pd


def start_2026_new_year_sale(testrun=True):
    client = utils.client("ssil")
    rows = client.worksheet_rows(
        sheet_id="1uYE0j-LZxRzkXbe1Hlp8eB1J02mKFdFirtogytSmfcY", sheet_title="シート1"
    )
    df = pd.DataFrame(columns=["title", "sku"], data=rows)
    skus = df["sku"].tolist()
    variants = [client.variant_by_sku(sku) for sku in skus]
    discounted_prices_by_variant_id = {
        v["id"]: int(int(v["price"]) * 0.85) for v in variants
    }
    client.update_variant_prices_by_dict(
        variants=variants,
        new_prices_by_variant_id=discounted_prices_by_variant_id,
        testrun=testrun,
    )


def end_2026_new_year_sale(testrun=True):
    client = utils.client("ssil")
    rows = client.worksheet_rows(
        sheet_id="1uYE0j-LZxRzkXbe1Hlp8eB1J02mKFdFirtogytSmfcY", sheet_title="シート1"
    )
    df = pd.DataFrame(columns=["title", "sku"], data=rows)
    skus = df["sku"].tolist()
    variants = [client.variant_by_sku(sku) for sku in skus]
    client.revert_variant_prices(variants, testrun=testrun)
