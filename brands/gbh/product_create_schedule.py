import logging
from brands.gbh.client import GbhClient, GbhClientColorOptionOnly, GbhCosmeticClient

logging.basicConfig(level=logging.INFO)

EXCLUDE_APPAREL_TITLES = ["GARDEN BAG SMALL", "TULIP BAG"]
EXCLUDE_COSMETIC_TITLES = ["DEEP CLEANSING SHAMPOO", "BODY WASH NEROLI MUSK"]
TAG = "26SS_3.10"

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


def create_26ss_color_only():
    client = GbhClientColorOptionOnly(product_sheet_start_row=1)
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    sheet_name = "26ss アパレル１次spring1차스프링오픈(COLOR ONLY)"
    filter_func = lambda pi: pi["title"] in EXCLUDE_APPAREL_TITLES

    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival", TAG],
        product_inputs_filter_func=filter_func
    )


def create_26ss_color_size():
    client = GbhClient(product_sheet_start_row=1)
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    sheet_name = "26ss アパレル１次spring1차스프링오픈(COLOR+SIZE)"
    filter_func = lambda pi: pi["title"] in EXCLUDE_APPAREL_TITLES

    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival", TAG],
        product_inputs_filter_func=filter_func
    )


def create_cosmetic():
    client = GbhCosmeticClient(product_sheet_start_row=1)
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    sheet_name = "新コスメ(코스메신상)3/10open"
    filter_func = lambda pi: pi["title"] not in EXCLUDE_COSMETIC_TITLES

    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival", TAG],
        product_inputs_filter_func=filter_func
    )


skus = [
    "APC1PT050MBS",
    "APC1PT050MBM",
    "APC1PT040IDS",
    "APC1PT040IDM",
    "APB3PT040IDS",
    "APB3PT040IDM",
    "APB3PT040BKS",
    "APB3PT040BKM",
    "APC1PT130WHS",
    "APC1PT130WHM",
    "APB3PT040KHS",
    "APB3PT040KHM",
    "APC1PT080BKS",
    "APC1PT080BKM",
    "APC1PT080BES",
    "APC1PT080BEM",
    "APA3JK040BKFF",
    "APB3JK010BRFF",
    "APC1CT020BEFF",
    "APC1TP110RDFF",
    "APC1TP110WHFF",
    "APC1TP110BKFF",
    "APC1TP060LBFF",
    "APC1TP060BLFF",
    "APC1TP060BKFF",
    "APC1TP150RDFF",
    "APC1TP150CRFF",
    "APC1TP150LBFF",
    "APC1TP150NYFF",
    "APC1SH020WHFF",
    "APB1KN030GYFF",
    "APB1KN030RDFF",
    "APB1KN030BKFF",
    "APB1KN030NYFF",
    "APC1KN030BUFF",
    "APB3KN070BKFF",
    "APB3KN070NYFF",
    "APB3KN070RDFF",
    "APB3KN070IVFF",
    "APC1KN040SBFF",
    "APC1CD010BPFF",
    "APC1CD010SBFF",
    "APC1CD010MGFF",
    "APC1CD010NYFF",
    "APC1CD010BKFF",
    "APC1CD010BSFF",
    "APC1CD010GSFF",
    "APB3BT020DWFF",
    "APB3AC070YEFF",
    "APB3AC070GRFF",
    "APB3AC070OLFF",
    "APB3AC070BLFF",
    "APB3AC070IVFF",
    "APB3AC070RDFF",
    "APB3AC070CHFF",
    "APB3AC070BKFF",
    "APC1AC020CHFF",
    "APC1AC020PUFF",
    "APC1AC020RDFF",
    "APC1AC030RDFF",
    "APC1AC030BKFF",
    "APC1AC030CHFF",
    "APC1AC030YEFF",
    "APC1AC030BRFF",
    "8800256755561",
    "8800256755936",
    "8809855950155",
    "APB1PT140BKS",
    "APB1PT140BKM",
    "APC1HZ020CHFF",
    "APC1HZ020BKFF",
    "APC1JP010WHFF",
    "APC1JP010KHFF",
    "APC1TP090BRFF",
    "APC1TP090NYFF",
    "APC1TP090MGFF",
    "APC1TP100GYFF",
    "APC1TP100BLFF",
    "APC1TP140GYFF",
    "APC1TP140BKFF",
    "APC1TP140WHFF",
    "APC1SK050WHFF",
    "APC1SK050CKFF",
    "APB3CD090IVFF",
    "APB3CD090MGFF",
    "APB3CD090RDFF",
    "APB3CD090OLFF",
    "APB3CD090BKFF",
    "APC1PT110BKFF",
    "APC1PT110RDFF",
    "APC1PT110BPFF",
    "APB3BG020BKFF",
    "APB3BG010CCFF",
    "APB3BG010BKFF",
    "APC1AC040IDFF",
    "APC1AC040BKFF",
    "APC1AC040CHFF",
    "APC1AC040RDFF",
    "APC1AC040BEFF",
    "APC1AC040WHFF",
]


def start_end_discounts(testrun=True, start_or_end="end"):
    client = GbhClient()
    variants = [client.variant_by_sku(sku) for sku in skus]
 
    if start_or_end == "end":
        client.revert_variant_prices(variants, testrun=testrun)
    else:
        new_prices_by_variant_id = {
            v["id"]: int(int(v["compareAtPrice"] or v["price"]) * 0.9)
            for v in variants
        }
        client.update_variant_prices_by_dict(
            variants, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
        )


def main():
    archive_apparel_products()
    archive_cosmetic_products()
    create_26ss_color_only()
    create_26ss_color_size()
    create_cosmetic()
    start_end_discounts(testrun=False, start_or_end="start")

if __name__ == "__main__":
    main()
