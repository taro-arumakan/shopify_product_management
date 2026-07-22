"""One-off ASHEIS shipping-rate setup (kept as a record; safe to re-run as a dry run).

EXECUTED 2026-07-22 against asheis.myshopify.com. Result: the single merchant
delivery profile ("General profile", one location group, 10 JP zones) now has
exactly ONE unconditional method per zone named `通常配送 (8/21より順次発送)` at the
confirmed per-region price below. The previous 20 methods were removed:
  - 10x `送料無料` (free when TOTAL_PRICE >= ¥10,000)
  - 10x `通常配送（地域）` (flat rate, conditioned to TOTAL_PRICE <= ¥9,999)
i.e. free shipping was removed and each zone's flat rate now applies to all order
values. Only 沖縄県 changed price (¥600 -> ¥1,500); every other zone kept its rate
but lost the free-shipping tier and the <=¥9,999 condition.

Source of truth: Google Sheet 1zSREOP7pEGIdyixl7Pz8_xN0tFUsN5K6j11J4LCM7NM,
worksheet "★送料" (gid 1968724936), option 2 (地域毎で設定); the 送料無料 section
was left blank, i.e. no free-shipping threshold. `rates_from_sheet()` re-reads it.

Why not helpers.shipping.update_delivery_flat_rate: that helper assumes the
conditional rate shares the base method's id with a "?" suffix and it preserves
the free-shipping method. ASHEIS's free-shipping rates are separate method
definitions, and here they must be deleted outright. So this deletes all methods
in each zone and creates one fresh unconditional flat rate, as a single atomic
deliveryProfileUpdate.

Usage:
    python -m brands.asheis.update_shipping             # dry run (no writes)
    python -m brands.asheis.update_shipping --execute   # apply
    python -m brands.asheis.update_shipping --from-sheet # dry run using live sheet
"""

import argparse
import json
import logging

import utils

logger = logging.getLogger(__name__)

NEW_METHOD_NAME = "通常配送 (8/21より順次発送)"

# Confirmed rates (JPY), keyed by the SHOPIFY delivery-zone name.
# The sheet header "沖縄" corresponds to the Shopify zone "沖縄県".
SHEET_RATES = {
    "北海道": 800,
    "東北": 600,
    "関東": 500,
    "信越・北陸": 500,
    "中部": 500,
    "関西": 500,
    "中国": 550,
    "四国": 550,
    "九州": 600,
    "沖縄県": 1500,
}

SHEET_ID = "1zSREOP7pEGIdyixl7Pz8_xN0tFUsN5K6j11J4LCM7NM"
SHEET_GID = 1968724936

PROFILE_QUERY = """
query {
  deliveryProfiles(first: 5, merchantOwnedOnly: true) {
    nodes {
      id name default
      profileLocationGroups {
        locationGroup { id }
        locationGroupZones(first: 20) {
          nodes {
            zone { id name }
            methodDefinitions(first: 10) {
              nodes {
                id name
                rateProvider { __typename ... on DeliveryRateDefinition { price { amount currencyCode } } }
                methodConditions { field operator conditionCriteria { __typename ... on MoneyV2 { amount } } }
              }
            }
          }
        }
      }
    }
  }
}
"""

UPDATE_MUTATION = """
mutation deliveryProfileUpdate($id: ID!, $profile: DeliveryProfileInput!) {
  deliveryProfileUpdate(id: $id, profile: $profile) {
    profile { id name }
    userErrors { field message }
  }
}
"""


def rates_from_sheet(client):
    """Re-read the confirmed per-region rates from the source spreadsheet.

    Expects worksheet "★送料": a header row listing the 10 region names and,
    two rows below it, the matching ¥ amounts (option 2, 地域毎で設定). The
    header "沖縄" is remapped to the Shopify zone name "沖縄県". Returns a dict
    keyed by Shopify zone name. Layout is fragile by nature; compare the result
    against SHEET_RATES before trusting it.
    """
    ss = client.gspread_client.open_by_key(SHEET_ID)
    ws = next((w for w in ss.worksheets() if w.id == SHEET_GID), None)
    if ws is None:
        raise RuntimeError(f"worksheet gid={SHEET_GID} not found")
    rows = ws.get_all_values()

    regions = [
        "北海道",
        "東北",
        "関東",
        "信越・北陸",
        "中部",
        "関西",
        "中国",
        "四国",
        "九州",
        "沖縄",
    ]
    header_idx = next(
        i for i, r in enumerate(rows) if all(reg in r for reg in regions[:3])
    )
    header = rows[header_idx]
    col = {r: header.index(r) for r in regions}
    # the ¥ amounts sit two rows below the header
    amounts = rows[header_idx + 2]

    def yen(cell):
        return int(cell.replace("¥", "").replace(",", "").strip())

    remap = {"沖縄": "沖縄県"}
    return {remap.get(r, r): yen(amounts[col[r]]) for r in regions}


def build_profile_input(profile, rates):
    """Return (profile_id, profile_input, plan_rows). Raises on zone mismatch."""
    loc_groups = profile["profileLocationGroups"]
    assert len(loc_groups) == 1, f"expected 1 location group, got {len(loc_groups)}"
    loc_group_id = loc_groups[0]["locationGroup"]["id"]
    zones = loc_groups[0]["locationGroupZones"]["nodes"]

    zone_names = {z["zone"]["name"] for z in zones}
    missing = [k for k in rates if k not in zone_names]
    unmatched = [z["zone"]["name"] for z in zones if z["zone"]["name"] not in rates]
    if missing or unmatched:
        raise RuntimeError(
            f"zone mapping mismatch — sheet-not-in-shopify={missing}, "
            f"shopify-not-in-sheet={unmatched}"
        )

    method_ids_to_delete = []
    zones_to_update = []
    plan_rows = []
    for z in zones:
        zname = z["zone"]["name"]
        new_price = rates[zname]
        old = []
        for m in z["methodDefinitions"]["nodes"]:
            method_ids_to_delete.append(m["id"])
            price = m["rateProvider"].get("price", {}).get("amount", "?")
            conds = "; ".join(
                f'{c["field"]} {c["operator"]} {c["conditionCriteria"].get("amount", "")}'
                for c in m.get("methodConditions", [])
            )
            old.append(f'{m["name"]} (¥{float(price):.0f}) [{conds or "no cond"}]')
        zones_to_update.append(
            {
                "id": z["zone"]["id"],
                "methodDefinitionsToCreate": [
                    {
                        "name": NEW_METHOD_NAME,
                        "active": True,
                        "rateDefinition": {
                            "price": {"amount": str(new_price), "currencyCode": "JPY"}
                        },
                    }
                ],
            }
        )
        plan_rows.append((zname, old, new_price))

    profile_input = {
        "methodDefinitionsToDelete": method_ids_to_delete,
        "locationGroupsToUpdate": [
            {"id": loc_group_id, "zonesToUpdate": zones_to_update}
        ],
    }
    return profile["id"], profile_input, plan_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute", action="store_true", help="apply the change (default: dry run)"
    )
    parser.add_argument(
        "--from-sheet",
        action="store_true",
        help="re-read rates from the sheet instead of SHEET_RATES",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    client = utils.client("asheis")

    rates = rates_from_sheet(client) if args.from_sheet else dict(SHEET_RATES)
    if args.from_sheet:
        logger.info("rates read from sheet: %s", rates)
        if rates != SHEET_RATES:
            logger.warning("sheet rates differ from the recorded SHEET_RATES constant!")

    profiles = client.run_query(PROFILE_QUERY)["deliveryProfiles"]["nodes"]
    assert len(profiles) == 1, f"expected 1 profile, got {len(profiles)}"
    profile_id, profile_input, plan_rows = build_profile_input(profiles[0], rates)

    print(
        f"PROFILE {profiles[0]['name']} ({profile_id}) | new method: {NEW_METHOD_NAME!r}"
    )
    for zname, old, new_price in plan_rows:
        print(f"\n■ {zname}")
        for d in old:
            print(f"    DELETE  {d}")
        print(f"    CREATE  {NEW_METHOD_NAME} (¥{new_price})  [no conditions]")
    print(
        f"\nzones={len(plan_rows)} "
        f"delete={len(profile_input['methodDefinitionsToDelete'])} "
        f"create={len(plan_rows)}"
    )

    if not args.execute:
        print("\nDRY RUN — no changes made. Re-run with --execute to apply.")
        return

    res = client.run_query(
        UPDATE_MUTATION, {"id": profile_id, "profile": profile_input}
    )
    errs = res["deliveryProfileUpdate"]["userErrors"]
    if errs:
        raise RuntimeError(f"userErrors: {json.dumps(errs, ensure_ascii=False)}")
    print(
        f"\n✅ Executed. Profile updated: {res['deliveryProfileUpdate']['profile']['name']}"
    )


if __name__ == "__main__":
    main()
