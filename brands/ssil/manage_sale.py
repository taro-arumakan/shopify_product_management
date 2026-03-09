import utils
import pandas as pd


def end_2026_gold_line(testrun=True):
    client = utils.client("ssil")
    products = client.products_by_query("tag:'26_gold_line'")
    client.revert_product_prices(products, testrun=testrun)


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


def start_end_new_clover_sale(testrun=True, start_or_end="end"):
    client = utils.client("ssil")
    # Collection: 3/12 NEW CLOVER
    products = client.products_by_collection_id("309971845213")

    if start_or_end == "end":
        client.revert_product_prices(products, testrun=testrun)
    else:
        new_prices_by_variant_id = {
            v["id"]: int(int(v["compareAtPrice"] or v["price"]) * 0.9)
            for p in products
            for v in p["variants"]["nodes"]
        }
        client.update_product_prices_by_dict(
            products, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
        )


if __name__ == "__main__":
    start_end_new_clover_sale()
