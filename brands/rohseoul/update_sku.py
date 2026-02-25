import logging
import utils

logging.basicConfig(level=logging.INFO)


_sku_mapping = {
    "JLL00CC6SBK": "JLL26CC6SBK",
    "JLL00CC6SUM": "JLL26CC6SUM",
    "JLL00CC7SBK": "JLL26CC7SBK",
    "JLL00CC7SUM": "JLL26CC7SUM",
    "JLL00CC7SIV": "JLL26SC7SIV",
    "JLL00CG8SBK": "JLL26CG8SBK",
    "JLL00CG8SUM": "JLL26CG8SUM",
    "JLL00CA2XBK": "JLL26CA2XBK",
    "JLL00CF1XBK": "JLL26CF1XBK",
    "JLL00C66SBK": "JLL26C66SBK",
    "JLL00C66SUM": "JLL26C66SUM",
    "JLL00CC1SBK": "JLL26CC1SBK",
    "JLL00CC1SIV": "JLL26SC1SIV",
    "JLL00C37NBK": "JLL26C37NBK",
    "JLL00C37NIV": "JLL26S37NIV",
    "JLL00CG4SBK": "JLL26CG4SBK",
    "JLL00CG4SUM": "JLL26CG4SUM",
    "JLL00CG5SBK": "JLL26CG5SBK",
    "JLL00CG5SIV": "JLL26SG5SIV",
    "JLL00CH0SBK": "JLL26CH0SBK",
    "JLL00CH0SBO": "JLL26SH0SBO",
    "JLL00CD0SBK": "JLL26CD0SBK",
    "JLL00CJ1PBK": "JLL26CJ1PBK",
    "JLL00CB5NBK": "JLL26CB5NBK",
    "JLL00CB5PBK": "JLL26CB5PBK",
    "JLL00CJ4SBK": "JLL26CJ4SBK",
    "JLL00CJ4SUM": "JLL26CJ4SUM",
    "JLL00CJ6SBK": "JLL26CJ6SBK",
    "JLL00CJ6SUM": "JLL26CJ6SUM",
    "JLL00CJ7SBK": "JLL26CJ7SBK",
    "JLL00CJ7SUM": "JLL26CJ7SUM",
    "JLL00CL2OBK": "JLL26CL2OBK",
    "JSL00CC9GBK": "JSL26SC9GBK",
    "JSL00CL1GBK": "JSL26SL1GBK",
    "JSL00C40SBK": "JSL26S40SBK",
    "JSL00C40SUM": "JSL26S40SUM",
    "JSL00C40VBK": "JSL26S40VBK",
    "JSL00C40VUM": "JSL26S40VUM",
    "JSL00C57SBK": "JSL26S57SBK",
    "JSL00C57SUM": "JSL26S57SUM",
    "JSL00C57VBK": "JSL26S57VBK",
    "JSL00C57VUM": "JSL26S57VUM",
    "JCL00CE7MBE": "JCL26SE7MBE",
    "JCL00C0BMNV": "JCL26S0BMNV",
    "JCL00C0BMMG": "JCL26S0BMMG",
    "JSM00C0DMBK": "JSM26S0DMBK",
    "JSM00C0DMBE": "JSM26S0DMBE",
    "JSM00C0EMIV": "JSM26S0EMIV",
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
