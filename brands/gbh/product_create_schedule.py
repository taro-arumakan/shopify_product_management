import logging
from brands.gbh.client import GbhClient, GbhClientColorOptionOnly, GbhCosmeticClient

logging.basicConfig(level=logging.INFO)

EXCLUDE_APPAREL_TITLES = ["SLIM FIT BASIC SLEEVELESS", "DRAWSTRING PANTS"]
EXCLUDE_COSMETIC_TITLES = []
TAG = "26SS_2nd"


def archive_apparel_products():
    client = GbhClient()
    for title in EXCLUDE_APPAREL_TITLES:
        product = client.product_by_title(title)
        client.archive_product(product)


def archive_cosmetic_products():
    client = GbhClient()
    for title in EXCLUDE_COSMETIC_TITLES:
        product = client.product_by_title(title)
        client.archive_product(product)


def create_26ss_2nd_color_only():
    client = GbhClientColorOptionOnly(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag=TAG,
    )
    sheet_name = "26ss アパレル2次spring2차스프링오픈(COLOR ONLY) "
    filter_func = lambda pi: pi["title"] in EXCLUDE_APPAREL_TITLES

    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival"],
        product_inputs_filter_func=filter_func,
    )


def create_cosmetic():
    client = GbhCosmeticClient(
        product_sheet_start_row=1, remove_existing_new_product_indicators=False
    )
    sheet_name = "新コスメ(코스메신상)3/10open"
    filter_func = lambda pi: pi["title"] in EXCLUDE_COSMETIC_TITLES

    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival", TAG],
        product_inputs_filter_func=filter_func,
    )


skus = [
    "APC1SL030WHFF",
    "APC1SL080BKFF",
    "APC1SL080NYFF",
    "APC1SL070RDFF",
    "APC1SL070OLFF",
    "APC1SL070BKFF",
    "APC1SL010BKFF",
    "APC1SL010BRFF",
    "APC1SL010WHFF",
    "APC1KN010BKFF",
    "APC1KN010BRFF",
    "APC1KN010WHFF",
    "APB3CD080BKFF",
    "APB3CD080NYFF",
    "APB3CD080RDFF",
    "APB3CD080IVFF",
    "APC1SK040WHFF",
    "APB1PT040RDFF",
    "APB2PT020BKFF",
    "8800256756995",
    "8800256757008",
    "8800256757015",
    "8800256757022",
    "8800256756834",
    "8800256756841",
    "8800256756858",
    "8800256756865",
    "8800256756919",
    "8800256756926",
    "8800256756933",
    "8800256756940",
    "8800256756957",
    "8800256756964",
    "8800256756971",
    "8800256756988",
    "8800256757077",
    "8800256757084",
    "8800256757091",
    "8800256757107",
    "8800256756872",
    "8800256756889",
    "8800256756896",
    "8800256756902",
    "8800256757114",
    "8800256757121",
    "8800256757138",
    "8800256757145",
    "8800256757039",
    "8800256757046",
    "8800256757053",
    "8800256757060",
    "8800256756353",
    "8800256756360",
    "8800256756377",
    "8800256756384",
    "8800256756193",
    "8800256756209",
    "8800256756216",
    "8800256756223",
    "8800256756278",
    "8800256756285",
    "8800256756292",
    "8800256756308",
    "8800256756315",
    "8800256756322",
    "8800256756339",
    "8800256756346",
    "8800256756438",
    "8800256756445",
    "8800256756452",
    "8800256756469",
    "8800256756230",
    "8800256756247",
    "8800256756254",
    "8800256756261",
    "8800256756476",
    "8800256756483",
    "8800256756490",
    "8800256756506",
    "8800256756391",
    "8800256756407",
    "8800256756414",
    "8800256756421",
    "8800256757312",
    "8800256757329",
    "8800256757336",
    "8800256757343",
    "8800256757152",
    "8800256757169",
    "8800256757176",
    "8800256757183",
    "8800256757237",
    "8800256757244",
    "8800256757251",
    "8800256757268",
    "8800256757275",
    "8800256757282",
    "8800256757299",
    "8800256757305",
    "8800256757398",
    "8800256757404",
    "8800256757411",
    "8800256757428",
    "8800256757190",
    "8800256757206",
    "8800256757213",
    "8800256757220",
    "800256757435",
    "8800256757442",
    "8800256757459",
    "8800256757466",
    "8800256757350",
    "8800256757367",
    "8800256757374",
    "8800256757381",
    "8800256756674",
    "8800256756681",
    "8800256756698",
    "8800256756704",
    "8800256756513",
    "8800256756520",
    "8800256756537",
    "8800256756544",
    "8800256756599",
    "8800256756605",
    "8800256756612",
    "8800256756629",
    "8800256756636",
    "8800256756643",
    "8800256756650",
    "8800256756667",
    "8800256756759",
    "8800256756766",
    "8800256756773",
    "8800256756780",
    "8800256756551",
    "8800256756568",
    "8800256756575",
    "8800256756582",
    "8800256756797",
    "8800256756803",
    "8800256756810",
    "8800256756827",
    "8800256756711",
    "8800256756728",
    "8800256756735",
    "8800256756742",
    "8800256756087",
    "8800256756025",
    "8800256756070",
    "8809855953804",
    "8800256756117",
    "8800256756131",
    "8809855951961",
    "8800256756032",
]


def start_end_discounts(testrun=True, start_or_end="end"):
    client = GbhClient()
    variants = client.variants_by_skus(skus)

    if start_or_end == "end":
        client.revert_variant_prices(variants, testrun=testrun)
    else:
        new_prices_by_variant_id = {
            v["id"]: int(int(v["compareAtPrice"] or v["price"]) * 0.9) for v in variants
        }
        client.update_variant_prices_by_dict(
            variants, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
        )


def add_selected_skus_to_collection():
    client = GbhClient()
    target_collection_id = "328576434375"
    target_skus = [
        "APB1PT040RDFF",
        "APB2PT020BKFF",
        "APC1SL070RDFF",
        "APC1SL070OLFF",
        "APC1SL070BKFF",
    ]
    product_ids = [client.product_id_by_sku(sku) for sku in target_skus]
    client.collection_add_products(target_collection_id, product_ids)


def main():
    archive_apparel_products()
    # archive_cosmetic_products()
    create_26ss_2nd_color_only()
    add_selected_skus_to_collection()
    # create_26ss_color_size()
    # create_cosmetic()
    start_end_discounts(testrun=False, start_or_end="start")


if __name__ == "__main__":
    main()
