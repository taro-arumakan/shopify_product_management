"""Detect and flag lememe orders shipping to an overseas package-forwarder address
(e.g. Buyandship), which the Korea->Japan personal-import lane cannot deliver. Matches
are tagged `forwarder-review` for CS to reroute (direct international ship / residential
JP address) rather than blocked — see the rerouting rule.

`evaluate_order` is a pure function so the same detection backs both the batch scan
(`ForwarderGuard.scan`, schedulable) and a per-order Shopify Flow / webhook call.

Run (from repo root):
    python -m brands.lememe.forwarder_guard                 # dry-run, recent orders
    python -m brands.lememe.forwarder_guard --since 2025-09-01
    python -m brands.lememe.forwarder_guard --since 2025-09-01 --apply   # actually tag
"""

import logging
import re
import unicodedata

from brands.lememe.forwarder_denylist import FORWARDER_HUBS, FORWARDER_CODE_PREFIXES

logger = logging.getLogger(__name__)

# Uppercase alphanumeric runs of length >= 6 (forwarder routing/member codes).
_CODE_RE = re.compile(r"[A-Z0-9]{6,}")


def _norm(s):
    return unicodedata.normalize("NFKC", s or "").strip()


def _norm_zip(s):
    return re.sub(r"\D", "", _norm(s))


def _code_tokens(text):
    """Uppercase alphanumeric runs of length >= 6 that are not purely digits."""
    return {t for t in _CODE_RE.findall(_norm(text).upper()) if not t.isdigit()}


def _shipping_name(ship):
    name = ship.get("name")
    if not name:
        name = " ".join(filter(None, [ship.get("firstName"), ship.get("lastName")]))
    return name or ""


def evaluate_order(order):
    """Forwarder detection over a Shopify order dict (Admin GraphQL shape).

    Returns {is_forwarder, service, confidence, reasons, signals}. No side effects.
    Triggers (any one flags the order): known forwarder hub, forwarder member-code
    prefix, or the same routing code repeated in both name and address. Billing-country
    mismatch is a supporting signal only, never a standalone trigger.
    """
    ship = order.get("shippingAddress") or {}
    bill = order.get("billingAddress") or {}

    name = _shipping_name(ship)
    address = " ".join(filter(None, [ship.get("address1"), ship.get("address2")]))
    zipc = _norm_zip(ship.get("zip"))
    norm_addr = _norm(address)

    reasons = []
    service = None

    # 1) Known forwarder warehouse (denylist) — highest precision.
    for hub in FORWARDER_HUBS:
        if (
            _norm_zip(hub["zip"]) == zipc
            and _norm(hub["address_contains"]) in norm_addr
        ):
            service = hub["service"]
            reasons.append(
                f"known forwarder hub: {hub['service']} ({hub['address_contains']} / {hub['zip']})"
            )
            break

    name_tokens = _code_tokens(name)
    addr_tokens = _code_tokens(address)

    # 2) Forwarder member-code prefix (e.g. Buyandship 'BS' + alphanumerics).
    for pref in FORWARDER_CODE_PREFIXES:
        p = pref["prefix"].upper()
        hits = sorted(
            t
            for t in (name_tokens | addr_tokens)
            if t.startswith(p) and len(t) >= len(p) + 5
        )
        if hits:
            service = service or pref["service"]
            reasons.append(f"{pref['service']} member code {hits[0]} on name/address")
            break

    # 3) Same routing code in BOTH name and address (generic forwarder signature).
    shared = sorted(name_tokens & addr_tokens)
    if shared:
        reasons.append(f"routing code {shared[0]} repeated in name & address")

    # Supporting signal (not a standalone trigger): billing country != shipping JP.
    ship_cc = (ship.get("countryCodeV2") or "").upper()
    bill_cc = (bill.get("countryCodeV2") or "").upper()
    billing_mismatch = bool(bill_cc and ship_cc == "JP" and bill_cc != "JP")
    if billing_mismatch and reasons:
        reasons.append(f"billing country {bill_cc} ≠ shipping JP")

    return {
        "is_forwarder": bool(reasons),
        "service": service,
        "confidence": "high" if service else ("medium" if reasons else "none"),
        "reasons": reasons,
        "signals": {"billing_mismatch": billing_mismatch},
    }


_SCAN_QUERY = """
query($first:Int!, $after:String, $q:String){
  orders(first:$first, after:$after, query:$q, sortKey:PROCESSED_AT, reverse:true){
    nodes{
      id name processedAt tags
      shippingAddress{ name firstName lastName company address1 address2 city zip countryCodeV2 }
      billingAddress{ countryCodeV2 }
    }
    pageInfo{ hasNextPage endCursor }
  }
}
"""


class ForwarderGuard:
    """Scan recent orders and tag the ones whose shipping address looks like an overseas
    package-forwarder (e.g. Buyandship), for CS rerouting review."""

    TAG = "forwarder-review"

    def __init__(self, client=None, shop_name="lememek"):
        if client is None:
            import utils
            from helpers.shopify_graphql_client.client import ShopifyGraphqlClient

            cred = utils.credentials(shop_name)
            client = ShopifyGraphqlClient(cred.shop_name, cred.access_token)
        self.client = client

    def _fetch_orders(self, processed_after=None, max_pages=20):
        q = f"processed_at:>='{processed_after}'" if processed_after else None
        orders, after, pages = [], None, 0
        while True:
            res = self.client.run_query(
                _SCAN_QUERY, {"first": 250, "after": after, "q": q}
            )
            data = res["orders"]
            orders.extend(data["nodes"])
            pages += 1
            if data["pageInfo"]["hasNextPage"] and pages < max_pages:
                after = data["pageInfo"]["endCursor"]
            else:
                break
        return orders

    def tags_for(self, ev):
        tags = [self.TAG]
        if ev["service"]:
            tags.append(f"forwarder-{ev['service'].lower()}")
        return tags

    def scan(self, processed_after=None, dry_run=True, max_pages=20):
        orders = self._fetch_orders(processed_after, max_pages)
        matched = []
        for order in orders:
            ev = evaluate_order(order)
            if not ev["is_forwarder"]:
                continue
            already = self.TAG in (order.get("tags") or [])
            matched.append((order, ev, already))
            logger.info(
                "%s%s  %s  ::  %s%s",
                "[DRY] " if dry_run else "",
                order["name"],
                ev["service"] or "forwarder",
                "; ".join(ev["reasons"]),
                "  (already tagged)" if already else "",
            )
            if not dry_run and not already:
                self.client.order_add_tags(order["id"], self.tags_for(ev))
        logger.info(
            "forwarder scan: scanned=%d matched=%d dry_run=%s",
            len(orders),
            len(matched),
            dry_run,
        )
        return matched


def main():
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Flag forwarder/Buyandship orders for CS rerouting review."
    )
    parser.add_argument(
        "--since", help="Only scan orders processed on/after this date (YYYY-MM-DD)."
    )
    parser.add_argument(
        "--apply", action="store_true", help="Add tags (default: dry-run, read-only)."
    )
    parser.add_argument(
        "--max-pages", type=int, default=20, help="Max pages of 250 orders to scan."
    )
    args = parser.parse_args()

    guard = ForwarderGuard()
    guard.scan(
        processed_after=args.since, dry_run=not args.apply, max_pages=args.max_pages
    )


if __name__ == "__main__":
    main()
