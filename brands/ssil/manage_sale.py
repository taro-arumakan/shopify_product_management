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


def start_end_2026_0814_summer_sale(testrun=True, start_or_end="start"):
    title_discount_map = {
        "Clover Safety Pin Choker": 0.85,
        "[G] CIRCLE CHAIN": 0.9,
        "2 LINE HOOPS_S": 0.85,
        "3 LINE HOOPS_S_C": 0.85,
        "CLOVER BAND R": 0.85,
        "X ROW R_M": 0.85,
        "Volume Heart String N": 0.75,
        "2 LINE HOOPS": 0.85,
        "X DOT CHAIN": 0.85,
        "X ROW R_S": 0.85,
        "X ROW HOOPS": 0.75,
        "X Safety Pin Choker": 0.85,
        "X ROW PEARL COLLAR": 0.7,
        "3 LINE HOOPS_L": 0.85,
        "CLASSIC BAND R_L": 0.75,
        "3 LINE HOOPS_L_C": 0.85,
        "Navy Clover Charm": 0.75,
        "LUCKY CLOVER LONG CHAIN": 0.7,
        "Circle Cross Hoops": 0.85,
        "[G] LUCKY DIA SILK BRACELET": 0.9,
        "Black Heart Charm": 0.85,
        "CLOVER PEARL LONG N": 0.7,
        "3 LINE HOOPS_S": 0.85,
        "X Safety Pin N": 0.85,
        "TWIST BOLD R": 0.85,
        "X ROW BRACELET": 0.85,
        "BLACK CLOVER BAND R": 0.85,
        "Clover Safety Pin Drop N": 0.85,
        "X LOGO E": 0.75,
        "RIM HOOPS": 0.85,
        "TIED X R": 0.85,
        "Clear Heart Charm": 0.75,
        "SLIM CLOVER BAND R": 0.85,
        "CLASSIC HOOPS_M": 0.75,
        "Circle Cross Charm_S": 0.75,
        "CLEAR CHAIN": 0.85,
        "[G] ANNEX SAFETY PIN": 0.9,
        "FLAT CLOVER 2 PENDANT": 0.85,
        "CLOVER DOT COLLAR": 0.7,
        "Two Tone Coin Pendant": 0.7,
        "2 PENDANT N_BALL": 0.75,
        "Square Clover Charm": 0.75,
        "Flat Heart Charm": 0.75,
        "LUCKY CLOVER STUDS": 0.75,
        "TINY TWIST BOLD E": 0.7,
        "STONE CLOVER STUDS_BLACK": 0.75,
        "Blue Clover Charm": 0.75,
        "CLASSIC HOOPS-S": 0.75,
        "STONE CLOVER STUDS_GREEN": 0.75,
        "[C] Gold Bar T-Shirt_Blue": 0.8,
        "[C] Gold Bar T-Shirt_Charcoal": 0.8,
        "[C] Pearl T-Shirt": 0.8,
        "Silver Ball Charm": 0.75,
        "[C] I H8 U T-Shirt_White": 0.8,
        "[C] I H8 U T-Shirt_Gray": 0.8,
        "[H] I H8 U Ball Cap": 0.8,
        "LUCKY CLOVER BAND R": 0.85,
        "PAVE X LINE R": 0.85,
        "Ball Clip Chain": 0.7,
        "TWIST BOLD E_S": 0.75,
        "[G] SIGNATURE PENDANT": 0.9,
        "TINY HOOPS_S": 0.5,
        "WATER DROP E_S": 0.85,
        "Pearl Cross Pendant_Chain": 0.85,
        "WATER DROP E_L": 0.85,
        "Slim X Row Chain": 0.85,
        "X ROW LAYER R": 0.85,
    }

    client = utils.client("ssil")
    products = []
    discount_by_product_id = {}
    for title, mult in title_discount_map.items():
        product = client.product_by_title(title)
        products.append(product)
        discount_by_product_id[product["id"]] = mult

    if start_or_end == "end":
        client.revert_product_prices(products, testrun=testrun)
    else:
        new_prices_by_variant_id = {
            v["id"]: int(
                int(v["compareAtPrice"] or v["price"]) * discount_by_product_id[p["id"]]
            )
            for p in products
            for v in p["variants"]["nodes"]
        }
        client.update_product_prices_by_dict(
            products, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
        )


if __name__ == "__main__":
    start_end_2026_0814_summer_sale(testrun=True, start_or_end="start")
