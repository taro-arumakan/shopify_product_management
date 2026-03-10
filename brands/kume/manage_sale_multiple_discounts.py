from brands.kume.client import KumeClient


def start_end_discounts(testrun=True, start_or_end="start"):
    """
    KUMÉ 3/16 26ss 2nd drop & 10% off
    """
    client = KumeClient()

    sku_discount_map = {
        # 26SS 2nd Drop
        "KM-26SS-BG01-BK-F": 0.9,
        "KM-26SS-BG01-KH-F": 0.9,
        "KM-26SS-BL02-BK-S": 0.9,
        "KM-26SS-BL02-BK-M": 0.9,
        "KM-26SS-BL02-BK-L": 0.9,
        "KM-26SS-BL02-IV-S": 0.9,
        "KM-26SS-BL02-IV-M": 0.9,
        "KM-26SS-BL02-IV-L": 0.9,
        "KM-26SS-BL04-BE-S": 0.9,
        "KM-26SS-BL04-BE-M": 0.9,
        "KM-26SS-BL04-BE-L": 0.9,
        "KM-26SS-BL04-MT-S": 0.9,
        "KM-26SS-BL04-MT-M": 0.9,
        "KM-26SS-BL04-MT-L": 0.9,
        "KM-26SS-BL05-BK-S": 0.9,
        "KM-26SS-BL05-BK-M": 0.9,
        "KM-26SS-BL05-BK-L": 0.9,
        "KM-26SS-BL05-WH-S": 0.9,
        "KM-26SS-BL05-WH-M": 0.9,
        "KM-26SS-BL05-WH-L": 0.9,
        "KM-26SS-BL06-IV-S": 0.9,
        "KM-26SS-BL06-IV-M": 0.9,
        "KM-26SS-BL06-IV-L": 0.9,
        "KM-26SS-OP01-IV-S": 0.9,
        "KM-26SS-OP01-IV-M": 0.9,
        "KM-26SS-OP01-IV-L": 0.9,
        "KM-26SS-OP01-NV-S": 0.9,
        "KM-26SS-OP01-NV-M": 0.9,
        "KM-26SS-OP01-NV-L": 0.9,
        "KM-26SS-OP02-LBE-S": 0.9,
        "KM-26SS-OP02-LBE-M": 0.9,
        "KM-26SS-OP02-LBE-L": 0.9,
        "KM-26SS-PT02-BK-S": 0.9,
        "KM-26SS-PT02-BK-M": 0.9,
        "KM-26SS-PT02-BK-L": 0.9,
        "KM-26SS-PT04-CH-S": 0.9,
        "KM-26SS-PT04-CH-M": 0.9,
        "KM-26SS-PT04-CH-L": 0.9,
        "KM-26SS-PT04-LKK-S": 0.9,
        "KM-26SS-PT04-LKK-M": 0.9,
        "KM-26SS-PT04-LKK-L": 0.9,
        "KM-26SS-SK04-BE-S": 0.9,
        "KM-26SS-SK04-BE-M": 0.9,
        "KM-26SS-SK04-BE-L": 0.9,
        "KM-26SS-SK04-BK-S": 0.9,
        "KM-26SS-SK04-BK-M": 0.9,
        "KM-26SS-SK04-BK-L": 0.9,
        "KM-26SS-SW03-IV-S": 0.9,
        "KM-26SS-SW03-IV-M": 0.9,
        "KM-26SS-SW03-IV-L": 0.9,
        "KM-26SS-SW03-LBL-S": 0.9,
        "KM-26SS-SW03-LBL-M": 0.9,
        "KM-26SS-SW03-LBL-L": 0.9,
        "KM-26SS-SW03-NV-S": 0.9,
        "KM-26SS-SW03-NV-M": 0.9,
        "KM-26SS-SW03-NV-L": 0.9,
        "KM-26SS-SW03-SK-S": 0.9,
        "KM-26SS-SW03-SK-M": 0.9,
        "KM-26SS-SW03-SK-L": 0.9,
        "KM-26SS-TS02-BU-S": 0.9,
        "KM-26SS-TS02-BU-M": 0.9,
        "KM-26SS-TS02-BU-L": 0.9,
        "KM-26SS-TS02-PK-S": 0.9,
        "KM-26SS-TS02-PK-M": 0.9,
        "KM-26SS-TS02-PK-L": 0.9,
        "KM-26SS-TS02-WH-S": 0.9,
        "KM-26SS-TS02-WH-M": 0.9,
        "KM-26SS-TS02-WH-L": 0.9,
        "M-KM-26SS-BL08-IV-L": 0.9,
        "M-KM-26SS-BL08-IV-XL": 0.9,
        "M-KM-26SS-BL08-NV-L": 0.9,
        "M-KM-26SS-BL08-NV-XL": 0.9,
        "M-KM-26SS-BL09-DBN-L": 0.9,
        "M-KM-26SS-BL09-DBN-XL": 0.9,
        "M-KM-26SS-PT08-LGR-M": 0.9,
        "M-KM-26SS-PT08-LGR-L": 0.9,
        "M-KM-26SS-PT08-LGR-XL": 0.9,
        "M-KM-26SS-SW06-GR-M": 0.9,
        "M-KM-26SS-SW06-GR-L": 0.9,
        "M-KM-26SS-SW06-GR-XL": 0.9,
        "M-KM-26SS-SW06-BK-M": 0.9,
        "M-KM-26SS-SW06-BK-L": 0.9,
        "M-KM-26SS-SW06-BK-XL": 0.9,
        "M-KM-26SS-SW06-IV-M": 0.9,
        "M-KM-26SS-SW06-IV-L": 0.9,
        "M-KM-26SS-SW06-IV-XL": 0.9,
        "M-KM-26SS-SW07-GR-M": 0.9,
        "M-KM-26SS-SW07-GR-L": 0.9,
        "M-KM-26SS-SW07-NV-M": 0.9,
        "M-KM-26SS-SW07-NV-L": 0.9,
        "M-KM-26SS-TS03-GR-M": 0.9,
        "M-KM-26SS-TS03-GR-L": 0.9,
        "M-KM-26SS-TS03-GR-XL": 0.9,
        "M-KM-26SS-TS03-NV-M": 0.9,
        "M-KM-26SS-TS03-NV-L": 0.9,
        "M-KM-26SS-TS03-NV-XL": 0.9,
        # 26SS 1st Drop
        "KM-26SS-BL07-IV-S": 0.95,
        "KM-26SS-BL07-IV-M": 0.95,
        "KM-26SS-BL07-IV-L": 0.95,
        "KM-26SS-JK01-IV-S": 0.95,
        "KM-26SS-JK01-IV-M": 0.95,
        "KM-26SS-JP01-CH-F": 0.95,
        "KM-26SS-JP01-IV-F": 0.95,
        "KM-26SS-JP01-OL-F": 0.95,
        "KM-26SS-PT05IVS": 0.95,
        "KM-26SS-PT05IVM": 0.95,
        "KM-26SS-PT05IVL": 0.95,
        "KM-26SS-PT05LBLS": 0.95,
        "KM-26SS-PT05LBLM": 0.95,
        "KM-26SS-PT05LBLL": 0.95,
        "KM-26SS-SK02ECS": 0.95,
        "KM-26SS-SK02ECM": 0.95,
        "KM-26SS-SK02ECL": 0.95,
        "KM-26SS-SK02IVS": 0.95,
        "KM-26SS-SK02IVM": 0.95,
        "KM-26SS-SK02IVL": 0.95,
        "KM-26SS-SK03IVS": 0.95,
        "KM-26SS-SK03IVM": 0.95,
        "KM-26SS-SK03IVL": 0.95,
        "KM-26SS-SW01BKS": 0.95,
        "KM-26SS-SW01BKM": 0.95,
        "KM-26SS-SW01BKL": 0.95,
        "KM-26SS-SW01IVS": 0.95,
        "KM-26SS-SW01IVM": 0.95,
        "KM-26SS-SW01IVL": 0.95,
        "KM-26SS-SW01MTS": 0.95,
        "KM-26SS-SW01MTM": 0.95,
        "KM-26SS-SW01MTL": 0.95,
        "KM-26SS-SW04BKS": 0.95,
        "KM-26SS-SW04BKM": 0.95,
        "KM-26SS-SW04BKL": 0.95,
        "KM-26SS-SW04IVS": 0.95,
        "KM-26SS-SW04IVM": 0.95,
        "KM-26SS-SW04IVL": 0.95,
        "KM-26SS-SW04MTS": 0.95,
        "KM-26SS-SW04MTM": 0.95,
        "KM-26SS-SW04MTL": 0.95,
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
