"""Stopgap: set approved per-category 'blanket' shipping weights on ACTIVE alvana product
variants that have NO weight, so the Japan Post carrier rate can calculate and international
checkout is unblocked. Only touches variants whose weight is missing/zero; never overwrites
an existing weight. Classification is by product title; UNMATCHED titles are skipped (not
guessed). Replace with measured weights later."""

import re
import utils

client = utils.client("alvana")
DRY_RUN = True


# Approved category -> shipping weight (kg, packaging included). Garment types are matched
# before accessories so e.g. "BELTED WIDE PANTS" -> Pants, not Belt.
def classify(title):
    t = title.upper()
    if any(k in t for k in ["LEATHER", "SUEDE", "SHEEPSKIN", "LAMBSKIN"]):
        return ("Leather jacket", 1.5)
    if "COAT" in t:  # 'COAT' is not a substring of 'COACH'
        return ("Coat", 1.3)
    if any(
        k in t
        for k in ["JACKET", " JK", "PARKA", "COVERALL", "COACH", "TRACKER", "BLAZER"]
    ):
        return ("Jacket/Parka/Coverall", 1.1)
    if any(k in t for k in ["KNIT", "CARDIGAN", "SWEAT", "HAORI"]):
        return ("Knit/Cardigan/Sweat", 0.55)
    if "SKIRT" in t:
        return ("Skirt", 0.5)
    if "SHORTS" in t or "SHORT PANTS" in t or "HALF PANTS" in t or "KNEE" in t:
        return ("Shorts", 0.45)
    if any(k in t for k in ["PANTS", "DENIM", "TROUSER", "SLACKS"]):
        return ("Pants/Denim", 0.7)
    if "CAP" in t or "HAT" in t:
        return ("Cap/Hat", 0.18)
    if "BAG" in t:
        return ("Bag", 0.5)
    if "BELT" in t:  # after pants, so "BELTED ... PANTS" is already handled
        return ("Belt", 0.25)
    if any(
        k in t for k in ["NECKLACE", "BRACELET", "RING", "EARRING", "PENDANT", "CHAIN"]
    ):
        return ("Accessory", 0.1)
    if "TEE" in t or "T-SHIRT" in t or "CUT SEW" in t or "CUTSEW" in t:
        if "L/S" in t or "LONG" in t or "MIDDLENECK" in t:
            return ("L/S cut-sew", 0.35)
        return ("S/S Tee/Tank/Vest", 0.28)
    if any(k in t for k in ["TANK", "SLEEVELESS", "NO SLEEVE", "VEST"]):
        return ("S/S Tee/Tank/Vest", 0.28)
    if any(k in t for k in ["SHIRT", "BLOUSE", "SKIPPER"]):
        return ("Shirts/Blouse", 0.45)
    if any(k in t for k in ["TOP", "PISTE", "PULLOVER"]):  # sleeved pullover top
        return ("Top (cut-sew)", 0.35)
    return (None, None)


def fetch_products():
    q = """query($after: String) {
      products(first: 100, after: $after, query: "status:active") {
        pageInfo { hasNextPage endCursor }
        nodes { id title status
          variants(first: 60) { nodes { sku inventoryItem { id measurement { weight { value unit } } } } } }
      }
    }"""
    out, after = [], None
    while True:
        r = client.run_query(q, {"after": after})["products"]
        out += r["nodes"]
        if not r["pageInfo"]["hasNextPage"]:
            break
        after = r["pageInfo"]["endCursor"]
    return out


def weight_value(v):
    w = ((v.get("inventoryItem") or {}).get("measurement") or {}).get("weight") or {}
    return w.get("value")  # None or 0 == missing


def main():
    prods = [p for p in fetch_products() if "(no image)" not in p["title"]]
    to_set, unmatched, skipped_ok = [], [], 0
    print(f"{'source':26} {'kg':>5}  miss/tot  product")
    for p in sorted(prods, key=lambda x: x["title"]):
        variants = p["variants"]["nodes"]
        miss = [
            v
            for v in variants
            if not weight_value(v) and (v.get("inventoryItem") or {}).get("id")
        ]
        if not miss:
            skipped_ok += 1
            continue
        # prefer the product's own existing weight (mixed products); else the blanket estimate
        existing = next((weight_value(v) for v in variants if weight_value(v)), None)
        if existing:
            target, source = existing, "existing"
        else:
            cat, kg = classify(p["title"])
            if not cat:
                unmatched.append(p["title"])
                print(
                    f"{'??? UNMATCHED':26} {'':>5}  {len(miss)}/{len(variants):<4}  {p['title']}"
                )
                continue
            target, source = kg, f"blanket:{cat}"
        print(f"{source:26} {target:>5}  {len(miss)}/{len(variants):<4}  {p['title']}")
        for v in miss:
            to_set.append((v["inventoryItem"]["id"], target, p["title"]))

    print(
        f"\n{'DRY RUN — ' if DRY_RUN else ''}products needing weight: {len({t[2] for t in to_set})}, "
        f"variants to set: {len(to_set)}, already-weighted products skipped: {skipped_ok}, "
        f"UNMATCHED (skipped): {len(unmatched)}"
    )
    if not DRY_RUN:
        for inv_id, target, title in to_set:
            client.update_inventory_item_weight(inv_id, target, unit="KILOGRAMS")
        print(f"set weight on {len(to_set)} variants")


if __name__ == "__main__":
    main()
