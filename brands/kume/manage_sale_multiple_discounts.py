from brands.kume.client import KumeClient


def start_end_discounts(testrun=True, start_or_end="start"):
    """
    KUMÉ 3/2-3/15 essential line & best
    """
    client = KumeClient()

    sku_discount_map = {
        # BEST - 5% off
        "KM-25SS-SK04-IV-L": 0.95,
        "KM-25SS-SK04-IV-M": 0.95,
        "KM-25SS-SK04-IV-S": 0.95,
        "KM-25SS-BL06-IV-M": 0.95,
        "KM-25SS-BL06-IV-S": 0.95,
        "KM-25SS-BL06-NV-M": 0.95,
        "KM-25SS-BL06-NV-S": 0.95,
        "KM-25SS-SW03-WH-S": 0.95,
        "KM-25SS-SW03-WH-M": 0.95,
        "KM-25SS-SW03-BK-S": 0.95,
        "KM-25SS-SW03-BK-M": 0.95,
        "KM-25SS-SW03-LYE-S": 0.95,
        "KM-25SS-SW03-LYE-M": 0.95,
        
        # CARRY OVER - 10% off
        "KM-25HS-SK01-IV-L": 0.9,
        "KM-25HS-SK01-IV-M": 0.9,
        "KM-25HS-SK01-IV-S": 0.9,
        "KM-25HS-SK01-PC-L": 0.9,
        "KM-25HS-SK01-PC-M": 0.9,
        "KM-25HS-SK01-PC-S": 0.9,
        "KM-25HS-BL01-BK-M": 0.9,
        "KM-25HS-BL01-BK-S": 0.9,
        "KM-25HS-BL01-IV-M": 0.9,
        "KM-25HS-BL01-IV-S": 0.9,
        "KM-25SS-BL01-WH-F": 0.9,
        
        # ESSENTIAL - 5% off
        "KM-25SS-BL01-LM-F": 0.95,
        "KM-25SS-BL01-SBL-F": 0.95,
        "KM-25SS-BL01-PK-F": 0.95,
        "KM-25SS-BL08-SBL-F": 0.95,
        "KM-25SS-BL08-BLS-F": 0.95,
        "KM-25SS-BL08-LM-F": 0.95,
        "KM-25SS-BL08-PK-F": 0.95,
        "KM-25SS-TS01-BK-M": 0.95,
        "KM-25SS-TS01-BK-S": 0.95,
        "KM-25SS-TS01-LYE-M": 0.95,
        "KM-25SS-TS01-LYE-S": 0.95,
        "KM-25SS-TS01-MGY-M": 0.95,
        "KM-25SS-TS01-MGY-S": 0.95,
        "KM-25SS-TS01-WH-M": 0.95,
        "KM-25SS-TS01-WH-S": 0.95,
        "KM-25SS-TS02-BK-M": 0.95,
        "KM-25SS-TS02-BK-S": 0.95,
        "KM-25SS-TS02-LYE-M": 0.95,
        "KM-25SS-TS02-LYE-S": 0.95,
        "KM-25SS-TS02-MOT-M": 0.95,
        "KM-25SS-TS02-MOT-S": 0.95,
        "KM-25SS-TS02-WH-M": 0.95,
        "KM-25SS-TS02-WH-S": 0.95,
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
