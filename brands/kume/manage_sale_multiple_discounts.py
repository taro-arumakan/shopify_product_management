from brands.kume.client import KumeClient


def start_end_discounts(testrun=True, start_or_end="start"):
    """
    KUMÉ 3/16 26ss 2nd drop & 10% off
    """
    client = KumeClient()

    sku_discount_map = {
        "M-KM-26SS-TS04-CH-M": 0.95,
        "M-KM-26SS-TS04-CH-L": 0.95,
        "M-KM-26SS-TS04-CH-XL": 0.95,
        "M-KM-26SS-TS04-IV-M": 0.95,
        "M-KM-26SS-TS04-IV-L": 0.95,
        "M-KM-26SS-TS04-IV-XL": 0.95,
        "M-KM-26SS-TS04-NV-M": 0.95,
        "M-KM-26SS-TS04-NV-L": 0.95,
        "M-KM-26SS-TS04-NV-XL": 0.95,

        "M-KM-26SS-SW08BEM": 0.95,
        "M-KM-26SS-SW08BEL": 0.95,
        "M-KM-26SS-SW08GRM": 0.95,
        "M-KM-26SS-SW08GRL": 0.95,
        "M-KM-26SS-SW08OLM": 0.95,
        "M-KM-26SS-SW08OLL": 0.95,
        "M-KM-26SS-SW08ORM": 0.95,
        "M-KM-26SS-SW08ORL": 0.95,

        "M-KM-26SS-JP02CHL": 0.95,
        "M-KM-26SS-JP02CHXL": 0.95,

        "M-KM-26SS-BL11DGRL": 0.95,
        "M-KM-26SS-BL11DGRXL": 0.95,
        "M-KM-26SS-BL11IVL": 0.95,
        "M-KM-26SS-BL11IVXL": 0.95,

        "M-KM-26SS-BL10LGRM": 0.95,
        "M-KM-26SS-BL10LGRL": 0.95,
        "M-KM-26SS-BL10LGRXL": 0.95,
        "M-KM-26SS-BL10PKM": 0.95,
        "M-KM-26SS-BL10PKL": 0.95,
        "M-KM-26SS-BL10PKXL": 0.95,

        "M-KM-25FW-PT06-BK-L": 0.9,
        "M-KM-25FW-PT06-BK-M": 0.9,
        "M-KM-25FW-PT06-BK-XL": 0.9,
        "M-KM-25FW-PT06-MBL-L": 0.9,
        "M-KM-25FW-PT06-MBL-M": 0.9,
        "M-KM-25FW-PT06-MBL-XL": 0.9,

        "KM-26SS-SW04BKS": 0.95,
        "KM-26SS-SW04BKM": 0.95,
        "KM-26SS-SW04BKL": 0.95,
        "KM-26SS-SW04IVS": 0.95,
        "KM-26SS-SW04IVM": 0.95,
        "KM-26SS-SW04IVL": 0.95,
        "KM-26SS-SW04MTS": 0.95,
        "KM-26SS-SW04MTM": 0.95,
        "KM-26SS-SW04MTL": 0.95,

        "KM-26SS-SW01BKS": 0.95,
        "KM-26SS-SW01BKM": 0.95,
        "KM-26SS-SW01BKL": 0.95,
        "KM-26SS-SW01IVS": 0.95,
        "KM-26SS-SW01IVM": 0.95,
        "KM-26SS-SW01IVL": 0.95,
        "KM-26SS-SW01MTS": 0.95,
        "KM-26SS-SW01MTM": 0.95,
        "KM-26SS-SW01MTL": 0.95,

        "KM-26SS-SK02ECS": 0.95,
        "KM-26SS-SK02ECM": 0.95,
        "KM-26SS-SK02ECL": 0.95,
        "KM-26SS-SK02IVS": 0.95,
        "KM-26SS-SK02IVM": 0.95,
        "KM-26SS-SK02IVL": 0.95,

        "KM-26SS-PT05IVS": 0.95,
        "KM-26SS-PT05IVM": 0.95,
        "KM-26SS-PT05IVL": 0.95,
        "KM-26SS-PT05LBLS": 0.95,
        "KM-26SS-PT05LBLM": 0.95,
        "KM-26SS-PT05LBLL": 0.95,

        "KM-26SS-PT04-CH-S": 0.95,
        "KM-26SS-PT04-CH-M": 0.95,
        "KM-26SS-PT04-CH-L": 0.95,
        "KM-26SS-PT04-LKK-S": 0.95,
        "KM-26SS-PT04-LKK-M": 0.95,
        "KM-26SS-PT04-LKK-L": 0.95,

        "KM-26SS-PT02-BK-S": 0.95,
        "KM-26SS-PT02-BK-M": 0.95,
        "KM-26SS-PT02-BK-L": 0.95,

        "KM-26SS-OP01-IV-S": 0.95,
        "KM-26SS-OP01-IV-M": 0.95,
        "KM-26SS-OP01-IV-L": 0.95,
        "KM-26SS-OP01-NV-S": 0.95,
        "KM-26SS-OP01-NV-M": 0.95,
        "KM-26SS-OP01-NV-L": 0.95,

        "KM-26SS-JP01-CH-F": 0.95,
        "KM-26SS-JP01-IV-F": 0.95,
        "KM-26SS-JP01-OL-F": 0.95,

        "KM-25SS-SW06-BK-M": 0.85,
        "KM-25SS-SW06-BK-S": 0.85,
        "KM-25SS-SW06-IV-M": 0.85,
        "KM-25SS-SW06-IV-S": 0.85,
        "KM-25SS-SW06-LYE-M": 0.85,
        "KM-25SS-SW06-LYE-S": 0.85,
        "KM-25SS-SW06-MBE-M": 0.85,
        "KM-25SS-SW06-MBE-S": 0.85,

        "KM-25SS-BG01-BK-F": 0.8,
        "KM-25SS-BG01-WH-F": 0.8,
        "KM-25SS-BG01-YL-F": 0.8,

        "KM-25FW-JK01-TBK-M": 0.8,
        "KM-25FW-JK01-TBK-S": 0.8,
        "KM-25FW-JK01-BK-M": 0.8,
        "KM-25FW-JK01-BK-S": 0.8,
    }

    skus = list(sku_discount_map.keys())
    variants = [client.variant_by_sku(sku) for sku in skus]
 
    if start_or_end == "end":
        client.revert_variant_prices(variants, testrun=testrun)
    else:
        new_prices_by_variant_id = {}
        for v in variants:
            sku = v["sku"]
            discount_rate = sku_discount_map[sku]
            base_price = int(v["compareAtPrice"] or v["price"])
            new_price = int(base_price * discount_rate)
            new_prices_by_variant_id[v["id"]] = new_price
        
        client.update_variant_prices_by_dict(
            variants, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
        )


def main():
    start_end_discounts(testrun=True, start_or_end="start")

if __name__ == "__main__":
    main()
