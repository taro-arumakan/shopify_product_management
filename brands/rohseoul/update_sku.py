import logging
import utils

logging.basicConfig(level=logging.INFO)


_sku_mapping = {
    "JLL00C37NIV": "RLL25S37NIV",
    "JLL00C37NUM": "RLL25S37NUM",
    "JLL00CB5NBK": "RLL25SB5NBK",
    "JLL00CB5NKA": "RLL25SB5NKA",
    "JLL00CB5NOT": "RLL25SB5NOT",
    "JLL00CC0SSM": "RLL25SC0SSM",
    "JLL00CC3NBK": "RLL25CC3NBK",
    "JLL00CC4NBK": "RLL25CC4NBK",
    "JLL00CC63BK": "RLL25SC63BK",
    "JLL00CC73BK": "RLL25SC73BK",
    "JLL00CG4NOT": "RLL25SG4NOT",
    "JLL00CG5NIV": "RLL25SG5NIV",
    "JLL00CH0SSM": "RLL25SH0SSM",
    "JLL00CJ1PBK": "RLL25CJ1PBK",
    "JLL00CJ1PUM": "RLL25SJ1PUM",
    "JLL00CJ2SBK": "RLL25CJ2SBK",
    "JLL00CJ2SOV": "RLL25SJ2SOV",
    "JLL24SC5FBK": "JLL00CC5FBK",
    "JLL24SC5FCT": "JLL00CC5FCT",
    "JLL24SC5FIV": "JLL00CC5FIV",
}
sku_mapping = {v: k for k, v in _sku_mapping.items()}

client = utils.client("rohseoul")
for sku_old, sku_new in sku_mapping.items():
    variant = client.variant_by_sku(sku_old)
    assert variant, f"Variant with SKU {sku_old} not found"
    variant_id = variant["id"]
    product_id = variant["product"]["id"]
    client.update_variant_sku_by_variant_id(
        product_id=product_id, variant_ids=[variant_id], skus=[sku_new]
    )
