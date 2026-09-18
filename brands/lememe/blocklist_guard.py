"""Detect and hold lememe orders placed by a blocklisted buyer (e.g. #LM-1273: the goods
were delivered after the payment had been cancelled, and the buyer went silent on the
re-payment). Disabling a customer record does not stop them checking out as a guest, so
matching is on what the order itself carries: the same customer record, e-mail, phone
number, or shipping / billing address.

The blocklist lives in Shopify, not here: this repository and its Action logs are
public. CS blocklists a buyer by tagging the incident ORDER `blocklist`; the e-mail,
phones and addresses on that order, plus the customer's saved addresses, are read at
run time. Removing the tag lifts the block. Log lines name orders and which signal
matched, never the values themselves.

Matches are tagged `blocklist-review` and their open fulfillment orders are put on hold,
so nothing ships until CS decides (collect the outstanding balance first, or cancel).
Holding rather than rejecting at checkout keeps a false positive — a family member, a
neighbour in the same building — to a delay instead of a lost sale. Draft orders are
skipped: staff created them on purpose, e.g. the invoice for the outstanding balance.

Newly-flagged orders are e-mailed to NOTIFYEES_LEMEME_ORDER_GUARDS, shared by every
order guard (see order_guards, which runs this scan from the Shopify Flow 'Order
created' trigger); a live scan refuses to start without it.

Addresses match on the same postcode plus the same house numbers (丁目・番地・号・room,
full-width or not, in any notation), where one may stop short of the other — so a
missing building / room number still matches, while another room in the same building
does not unless the blocklisted address itself had no room number.

Run (from repo root):
    python -m brands.lememe.blocklist_guard                 # dry-run, active orders
    python -m brands.lememe.blocklist_guard --apply         # tag + hold + notify
    python -m brands.lememe.blocklist_guard --include-closed   # historical audit (dry)
"""

import logging
import re

from brands.lememe.forwarder_guard import _norm, _norm_zip
from brands.lememe.order_guards import recipients

logger = logging.getLogger(__name__)

_KANJI_DIGITS = {c: i for i, c in enumerate("〇一二三四五六七八九")}
_KANJI_CHOME_RE = re.compile(r"([〇一二三四五六七八九十]+)丁目")


def _kanji_to_int(s):
    """一 .. 九十九, which covers 丁目 numbers."""
    tens, sep, ones = s.partition("十")
    if not sep:
        return int("".join(str(_KANJI_DIGITS[c]) for c in s))
    return _KANJI_DIGITS.get(tens, 1) * 10 + _KANJI_DIGITS.get(ones, 0)


def _house_numbers(*lines):
    """The address's numbers in order: 'x1丁目2番地3号 ハイツ101' -> (1, 2, 3, 101)."""
    text = _norm(" ".join(filter(None, lines)))
    text = _KANJI_CHOME_RE.sub(lambda m: f"{_kanji_to_int(m.group(1))}丁目", text)
    return tuple(int(n) for n in re.findall(r"\d+", text))


def _norm_email(s):
    return _norm(s).lower() or None


def _norm_phone(s):
    """Digits only, +81 folded to a leading 0. Too short to be a number -> None."""
    digits = re.sub(r"\D", "", _norm(s))
    if digits.startswith("81") and len(digits) in (11, 12):
        digits = "0" + digits[2:]
    return digits if len(digits) >= 10 else None


def _address_key(addr):
    addr = addr or {}
    return _norm_zip(addr.get("zip")), _house_numbers(
        addr.get("address1"), addr.get("address2")
    )


def _emails(order):
    customer = order.get("customer") or {}
    candidates = [
        order.get("email"),
        (customer.get("defaultEmailAddress") or {}).get("emailAddress"),
    ]
    return {e for e in map(_norm_email, candidates) if e}


def _phones(order):
    customer = order.get("customer") or {}
    candidates = [
        order.get("phone"),
        (customer.get("defaultPhoneNumber") or {}).get("phoneNumber"),
        (order.get("shippingAddress") or {}).get("phone"),
        (order.get("billingAddress") or {}).get("phone"),
    ]
    return {p for p in map(_norm_phone, candidates) if p}


def build_blocklist(source_orders):
    """Signals to match against, from the orders CS tagged `blocklist`. Every signal maps
    to its source order's name, so a match can say which incident it repeats."""
    blocklist = {"customers": {}, "emails": {}, "phones": {}, "addresses": []}
    for src in source_orders:
        ref = src["name"]
        customer = src.get("customer") or {}
        if customer.get("id"):
            blocklist["customers"].setdefault(customer["id"], ref)
        for email in _emails(src):
            blocklist["emails"].setdefault(email, ref)
        for phone in _phones(src):
            blocklist["phones"].setdefault(phone, ref)
        saved = (customer.get("addressesV2") or {}).get("nodes") or []
        for addr in [src.get("shippingAddress"), src.get("billingAddress"), *saved]:
            if not addr:
                continue
            zipc, numbers = _address_key(addr)
            if zipc and numbers:
                blocklist["addresses"].append((zipc, numbers, ref))
            if phone := _norm_phone(addr.get("phone")):
                blocklist["phones"].setdefault(phone, ref)
    return blocklist


def _address_match(addr, blocked_addresses):
    zipc, numbers = _address_key(addr)
    if not (zipc and numbers):
        return None
    for blocked_zip, blocked_numbers, ref in blocked_addresses:
        n = min(len(numbers), len(blocked_numbers))
        if blocked_zip == zipc and numbers[:n] == blocked_numbers[:n]:
            return ref
    return None


def evaluate_order(order, blocklist):
    """Blocklist check over a Shopify order dict (Admin GraphQL shape).

    Returns {is_blocked, matches: {signal: source order name}, reasons}. No side
    effects. Any one signal flags the order.
    """
    matches = {}
    customer_id = (order.get("customer") or {}).get("id")
    if ref := blocklist["customers"].get(customer_id):
        matches["customer record"] = ref
    for email in sorted(_emails(order)):
        if ref := blocklist["emails"].get(email):
            matches.setdefault("e-mail", ref)
    for phone in sorted(_phones(order)):
        if ref := blocklist["phones"].get(phone):
            matches.setdefault("phone", ref)
    for signal, key in (
        ("shipping address", "shippingAddress"),
        ("billing address", "billingAddress"),
    ):
        if ref := _address_match(order.get(key), blocklist["addresses"]):
            matches[signal] = ref

    return {
        "is_blocked": bool(matches),
        "matches": matches,
        "reasons": [f"{signal} matches {ref}" for signal, ref in matches.items()],
    }


_ADDRESS_FIELDS = "address1 address2 zip phone"

_BLOCKLIST_QUERY = f"""
query($first:Int!, $after:String, $q:String){{
  orders(first:$first, after:$after, query:$q){{
    nodes{{
      id name tags email phone
      customer{{
        id
        defaultEmailAddress{{ emailAddress }}
        defaultPhoneNumber{{ phoneNumber }}
        addressesV2(first:10){{ nodes{{ {_ADDRESS_FIELDS} }} }}
      }}
      shippingAddress{{ {_ADDRESS_FIELDS} }}
      billingAddress{{ {_ADDRESS_FIELDS} }}
    }}
    pageInfo{{ hasNextPage endCursor }}
  }}
}}
"""

_SCAN_QUERY = f"""
query($first:Int!, $after:String, $q:String){{
  orders(first:$first, after:$after, query:$q, sortKey:PROCESSED_AT, reverse:true){{
    nodes{{
      id name processedAt tags sourceName email phone
      customer{{
        id
        defaultEmailAddress{{ emailAddress }}
        defaultPhoneNumber{{ phoneNumber }}
      }}
      shippingAddress{{ {_ADDRESS_FIELDS} }}
      billingAddress{{ {_ADDRESS_FIELDS} }}
    }}
    pageInfo{{ hasNextPage endCursor }}
  }}
}}
"""


class BlocklistGuard:
    """Scan recent orders and hold the ones placed by a blocklisted buyer, for CS
    review before anything ships."""

    SOURCE_TAG = "blocklist"
    TAG = "blocklist-review"
    HOLD_HANDLE = "blocklist-guard"

    _recipients = staticmethod(recipients)

    def __init__(self, client=None, shop_name="lememek"):
        if client is None:
            import utils
            from helpers.shopify_graphql_client.client import ShopifyGraphqlClient

            cred = utils.credentials(shop_name)
            client = ShopifyGraphqlClient(cred.shop_name, cred.access_token)
        self.client = client

    def _paginate(self, query, q, first, max_pages):
        orders, after, pages = [], None, 0
        while True:
            res = self.client.run_query(query, {"first": first, "after": after, "q": q})
            data = res["orders"]
            orders.extend(data["nodes"])
            pages += 1
            if data["pageInfo"]["hasNextPage"] and pages < max_pages:
                after = data["pageInfo"]["endCursor"]
            else:
                break
        return orders

    def _fetch_blocklist_sources(self):
        orders = self._paginate(
            _BLOCKLIST_QUERY, f"tag:'{self.SOURCE_TAG}'", first=50, max_pages=10
        )
        # The search matches tags loosely; keep exact ones only.
        return [o for o in orders if self.SOURCE_TAG in (o.get("tags") or [])]

    def _fetch_orders(self, processed_after=None, max_pages=20, active_only=True):
        clauses = []
        if active_only:
            clauses.append("status:'open'")
        if processed_after:
            clauses.append(f"processed_at:>='{processed_after}'")
        q = " AND ".join(clauses) or None
        return self._paginate(_SCAN_QUERY, q, first=250, max_pages=max_pages)

    def _hold(self, order, ev):
        """Hold each open fulfillment order. Failures are collected, not raised: the
        order is tagged and CS told either way, and the e-mail says what to do by hand.
        """
        outcome = {"held": 0, "not_open": [], "errors": []}
        notes = f"Blocklist match ({'; '.join(ev['reasons'])}). Check with CS before shipping."
        for fo in self.client.order_fulfillment_orders(order["id"]):
            if fo["status"] != "OPEN":
                outcome["not_open"].append(fo["status"])
                continue
            try:
                self.client.fulfillment_order_hold(
                    fo["id"],
                    reason="OTHER",
                    reason_notes=notes,
                    handle=self.HOLD_HANDLE,
                )
                outcome["held"] += 1
            except Exception as e:
                logger.warning("%s: could not hold %s: %s", order["name"], fo["id"], e)
                outcome["errors"].append(str(e))
        return outcome

    def _admin_url(self, order):
        return (
            f"https://admin.shopify.com/store/{self.client.shop_name}"
            f"/orders/{order['id'].rsplit('/', 1)[-1]}"
        )

    # Fulfillment order statuses that can still ship but were not held (only OPEN ones
    # are); ON_HOLD / CLOSED / CANCELLED need nothing.
    _SHIPPABLE_UNHELD = {"SCHEDULED", "IN_PROGRESS"}

    @classmethod
    def _describe_hold(cls, outcome):
        parts = []
        if outcome["held"]:
            parts.append(f"held {outcome['held']} fulfillment order(s)")
        if outcome["not_open"]:
            parts.append(f"left as is: {', '.join(outcome['not_open'])}")
        if outcome["errors"]:
            parts.append(f"HOLD FAILED ({'; '.join(outcome['errors'])})")
        if outcome["errors"] or cls._SHIPPABLE_UNHELD & set(outcome["not_open"]):
            parts.append("STOP THE SHIPMENT BY HAND")
        return " / ".join(parts) or "no fulfillment orders"

    def _notify(self, newly_flagged):
        from helpers.client import send_smtp_email

        to_addrs = self._recipients()
        blocks = [
            f"{order['name']}  {'; '.join(ev['reasons'])}\n"
            f"  {self._describe_hold(outcome)}\n"
            f"  {self._admin_url(order)}"
            for order, ev, outcome in newly_flagged
        ]
        body = (
            f"{len(newly_flagged)} order(s) matched the blocklist (tag: {self.TAG}). "
            "Collect the outstanding balance or cancel before shipping; release the "
            "hold from the order page once cleared.\n\n" + "\n\n".join(blocks)
        )
        send_smtp_email(
            subject=f"[lememe] {len(newly_flagged)} order(s) held: blocklist match",
            body=body,
            to_addrs=to_addrs,
        )

    def scan(self, processed_after=None, dry_run=True, max_pages=20, active_only=True):
        if not dry_run:
            # Check before holding anything, for the same reason as the forwarder
            # guard: the notify call below swallows its errors.
            self._recipients()
        sources = self._fetch_blocklist_sources()
        if not sources:
            logger.info("no orders tagged %r; nothing to match", self.SOURCE_TAG)
            return []
        blocklist = build_blocklist(sources)
        orders = self._fetch_orders(processed_after, max_pages, active_only=active_only)
        matched = []
        newly_flagged = []
        for order in orders:
            tags = order.get("tags") or []
            if (
                self.SOURCE_TAG in tags
                or order.get("sourceName") == "shopify_draft_order"
            ):
                continue
            ev = evaluate_order(order, blocklist)
            if not ev["is_blocked"]:
                continue
            already = self.TAG in tags
            matched.append((order, ev, already))
            logger.info(
                "%s%s  ::  %s%s",
                "[DRY] " if dry_run else "",
                order["name"],
                "; ".join(ev["reasons"]),
                "  (already tagged)" if already else "",
            )
            if dry_run or already:
                continue
            try:
                outcome = self._hold(order, ev)
                self.client.order_add_tags(order["id"], [self.TAG])
            except Exception:
                # Untagged, so the next run tries again.
                logger.exception("failed to hold/tag %s", order["name"])
                continue
            newly_flagged.append((order, ev, outcome))
        if newly_flagged:
            try:
                self._notify(newly_flagged)
            except Exception:
                logger.exception("failed to send blocklist notification email")
        logger.info(
            "blocklist scan: sources=%d scanned=%d matched=%d dry_run=%s active_only=%s",
            len(sources),
            len(orders),
            len(matched),
            dry_run,
            active_only,
        )
        return matched


def scan_blocklisted_orders(
    dry_run=False, processed_after=None, max_pages=20, active_only=True
):
    logging.basicConfig(level=logging.INFO)
    return BlocklistGuard().scan(
        processed_after=processed_after,
        dry_run=dry_run,
        max_pages=max_pages,
        active_only=active_only,
    )


def main():
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Hold orders placed by blocklisted buyers for CS review."
    )
    parser.add_argument(
        "--since", help="Only scan orders processed on/after this date (YYYY-MM-DD)."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Tag and hold matches (default: dry-run, read-only).",
    )
    parser.add_argument(
        "--max-pages", type=int, default=20, help="Max pages of 250 orders to scan."
    )
    parser.add_argument(
        "--include-closed",
        action="store_true",
        help="Also scan closed/cancelled orders (default: open/active orders only).",
    )
    args = parser.parse_args()

    scan_blocklisted_orders(
        processed_after=args.since,
        dry_run=not args.apply,
        max_pages=args.max_pages,
        active_only=not args.include_closed,
    )


if __name__ == "__main__":
    main()
