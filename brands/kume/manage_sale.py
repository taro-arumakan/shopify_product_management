from brands.kume.client import KumeClient


def start_end_discounts(testrun=True, start_or_end="start"):
    """
    26ss 1st drop sale (2/6~2/15) 
    """
    client = KumeClient()
    
    skus = [
        "KM-26SS-JK01-IV-S",
        "KM-26SS-JK01-IV-M",
        "KM-26SS-JP01-IV-F",
        "KM-26SS-JP01-OL-F",
        "KM-26SS-JP01-CH-F",
        "M-KM-26SS-JP02GRL",
        "M-KM-26SS-JP02GRXL",
        "M-KM-26SS-JP02CHL",
        "M-KM-26SS-JP02CHXL",
        "M-KM-26SS-TS04-IV-M",
        "M-KM-26SS-TS04-IV-L",
        "M-KM-26SS-TS04-IV-XL",
        "M-KM-26SS-TS04-OAT-M",
        "M-KM-26SS-TS04-OAT-L",
        "M-KM-26SS-TS04-OAT-XL",
        "M-KM-26SS-TS04-CH-M",
        "M-KM-26SS-TS04-CH-L",
        "M-KM-26SS-TS04-CH-XL",
        "M-KM-26SS-TS04-NV-M",
        "M-KM-26SS-TS04-NV-L",
        "M-KM-26SS-TS04-NV-XL",
        "KM-26SS-BL07-IV-S",
        "KM-26SS-BL07-IV-M",
        "KM-26SS-BL07-IV-L",
        "M-KM-26SS-BL10LGRM",
        "M-KM-26SS-BL10LGRL",
        "M-KM-26SS-BL10LGRXL",
        "M-KM-26SS-BL10PKM",
        "M-KM-26SS-BL10PKL",
        "M-KM-26SS-BL10PKXL",
        "M-KM-26SS-BL11IVL",
        "M-KM-26SS-BL11IVXL",
        "M-KM-26SS-BL11DGRL",
        "M-KM-26SS-BL11DGRXL",
        "KM-26SS-SW01IVS",
        "KM-26SS-SW01IVM",
        "KM-26SS-SW01IVL",
        "KM-26SS-SW01MTS",
        "KM-26SS-SW01MTM",
        "KM-26SS-SW01MTL",
        "KM-26SS-SW01BKS",
        "KM-26SS-SW01BKM",
        "KM-26SS-SW01BKL",
        "KM-26SS-SW04IVS",
        "KM-26SS-SW04IVM",
        "KM-26SS-SW04IVL",
        "KM-26SS-SW04MTS",
        "KM-26SS-SW04MTM",
        "KM-26SS-SW04MTL",
        "KM-26SS-SW04BKS",
        "KM-26SS-SW04BKM",
        "KM-26SS-SW04BKL",
        "M-KM-26SS-SW08BEM",
        "M-KM-26SS-SW08BEL",
        "M-KM-26SS-SW08ORM",
        "M-KM-26SS-SW08ORL",
        "M-KM-26SS-SW08OLM",
        "M-KM-26SS-SW08OLL",
        "M-KM-26SS-SW08GRM",
        "M-KM-26SS-SW08GRL",
        "KM-26SS-SK02ECS",
        "KM-26SS-SK02ECM",
        "KM-26SS-SK02ECL",
        "KM-26SS-SK02IVS",
        "KM-26SS-SK02IVM",
        "KM-26SS-SK02IVL",
        "KM-26SS-SK03IVS",
        "KM-26SS-SK03IVM",
        "KM-26SS-SK03IVL",
        "KM-26SS-PT05IVS",
        "KM-26SS-PT05IVM",
        "KM-26SS-PT05IVL",
        "KM-26SS-PT05LBLS",
        "KM-26SS-PT05LBLM",
        "KM-26SS-PT05LBLL",
        "M-KM-26SS-PT07ECM",
        "M-KM-26SS-PT07ECL",
        "M-KM-26SS-PT07ECXL",
        "M-KM-26SS-PT07BEM",
        "M-KM-26SS-PT07BEL",
        "M-KM-26SS-PT07BEXL",
        "M-KM-26SS-PT07CHM",
        "M-KM-26SS-PT07CHL",
        "M-KM-26SS-PT07CHXL",
    ]

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
    start_end_discounts(testrun=True, start_or_end="start")

if __name__ == "__main__":
    main()
