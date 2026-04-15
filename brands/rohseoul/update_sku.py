import logging
import utils

logging.basicConfig(level=logging.INFO)


sku_mapping = {
    "JLL00CC6NBK": "JLL26CC6NBK",
    "JLL00CC6NUM": "JLL26CC6NUM",
    "JLL00CC7NBK": "JLL26CC7NBK",
    "JLL00CC7NUM": "JLL26CC7NUM",
    "JLL00CC7NIV": "JLL26SC7NIV",
    "JLL00CG8NUM": "JLL26CG8NUM",
    "JLL00CG8NBK": "JLL26CG8NBK",
    "JLL00CG4NBK": "JLL26SG4NBK",
    "JLL00CG5NBK": "JLL26SG5NBK",
    "JLL00CC4NBK": "JLL26CC4NBK",
}

client = utils.client("rohseoul")
for sku_old, sku_new in sku_mapping.items():
    variant = client.variant_by_sku(sku_old)
    assert variant, f"Variant with SKU {sku_old} not found"
    variant_id = variant["id"]
    product_id = variant["product"]["id"]
    client.update_variant_sku_by_variant_id(
        product_id=product_id, variant_ids=[variant_id], skus=[sku_new]
    )
