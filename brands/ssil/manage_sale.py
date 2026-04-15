import logging

logging.basicConfig(level=logging.INFO)

import pandas as pd
import utils


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
    variants = client.variants_by_skus(skus)
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
    variants = client.variants_by_skus(skus)
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


def start_end_best_products_sale(testrun=True, start_or_end="end"):
    skus = [
        "SS24SRC200CG009ZZ",
        "SS23FNC006CS011ZZ",
        "SS23FNC006CS013ZZ",
        "SS23FNC006CS015ZZ",
        "SS23FNC006CS017ZZ",
        "SS24SRC207CG019ZZ",
        "24FEES09CBLL",
        "24FEES09WBLL",
        "24FEES09YBLL",
        "24FEES10CBSS",
        "24FEES10WBSS",
        "24FEES10YBSS",
        "SS20FEX005WBXXXMT",
        "SS20FEX005YBXXXMT",
        "24FRES03WS11",
        "24FRES03WS13",
        "24FRES03WS15",
        "24FRES03WS17",
        "24FRES03WS19",
        "24FRES02WS09",
        "24FRES02WS11",
        "24FRES02WS13",
        "24FRES02WS15",
        "24FRES02WS17",
        "24FRES02WS19",
        "24FRES02YS09",
        "24FRES02YS11",
        "24FRES02YS13",
        "24FRES02YS15",
        "24FRES02YS17",
        "24FRES02YS19",
        "24FRES01WS09",
        "24FRES01WS11",
        "24FRES01WS13",
        "24FRES01WS15",
        "24FRES01WS17",
        "24FRES01WS19",
        "24FRES01YS09",
        "24FRES01YS11",
        "24FRES01YS13",
        "24FRES01YS15",
        "24FRES01YS17",
        "24FRES01YS19",
        "SS24SNC039WGLLLMT",
        "25FNHR01WBFF",
        "SS24SNC027WGFFFMT",
        "SS24SNC027YGFFFMT",
        "SS24SNC041WGFFFMT",
        "SS24SNC041YGFFFMT",
        "24FECV02WBFF",
        "25SNCV03WBFF",
        "25SNCV03YBFF",
        "25SNES01NNSS",
        "25SNES01CSFF",
        "SS24SNC041WGFFFMT",
        "SS24SNC041YGFFFMT",
        "25FNBA09WSFF",
        "25FNBA09YSFF",
        "25SRCV02WS11",
        "25SRCV02WS13",
        "25SRCV02WS15",
        "25SRCV02YS11",
        "25SRCV02YS13",
        "25SRCV02YS15",
    ]

    client = utils.client("ssil")
    variants = client.variants_by_skus(set(skus))

    if start_or_end == "end":
        client.revert_variant_prices(variants=variants, testrun=testrun)
    else:
        new_prices_by_variant_id = {
            v["id"]: int(int(v["compareAtPrice"] or v["price"]) * 0.8) for v in variants
        }
        client.update_variant_prices_by_dict(
            variants=variants,
            new_prices_by_variant_id=new_prices_by_variant_id,
            testrun=testrun,
        )


if __name__ == "__main__":
    start_end_best_products_sale(testrun=False, start_or_end="start")
