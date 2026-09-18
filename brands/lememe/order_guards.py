"""Run every lememe order guard in one shot — the Shopify Flow 'Order created' trigger
dispatches `run_order_guards` through the run_func workflow:

    blocklist_guard   hold orders placed by blocklisted buyers
    forwarder_guard   flag orders shipping to an overseas package forwarder

Each guard e-mails its own findings to NOTIFYEES_LEMEME_ORDER_GUARDS (comma-separated:
the CATAL admin plus the LEMEME Korea staff who ship the orders). There is no default —
this repository is public — so a live run checks for it before touching any order.

One guard failing does not stop the other; the run still fails afterwards so the
Action shows red.

Run (from repo root):
    python -m brands.lememe.order_guards            # dry-run, active orders
    python -m brands.lememe.order_guards --apply    # tag / hold + notify
"""

import logging
import os

logger = logging.getLogger(__name__)

NOTIFYEES_ENV = "NOTIFYEES_LEMEME_ORDER_GUARDS"


def recipients():
    """Addresses from NOTIFYEES_LEMEME_ORDER_GUARDS. No default: this repo is public."""
    raw = os.environ.get(NOTIFYEES_ENV, "")
    addrs = [a.strip() for a in raw.split(",") if a.strip()]
    if not addrs:
        raise RuntimeError(
            f"{NOTIFYEES_ENV} is unset or empty — tagging orders that nobody "
            "is told about is worse than not scanning."
        )
    return addrs


def run_order_guards(
    dry_run=False, processed_after=None, max_pages=20, active_only=True, client=None
):
    # Imported here: the guards import `recipients` from this module.
    from brands.lememe.blocklist_guard import BlocklistGuard
    from brands.lememe.forwarder_guard import ForwarderGuard

    logging.basicConfig(level=logging.INFO)
    blocklist = BlocklistGuard(client=client)
    guards = {
        # Blocklist first: it holds orders, so it is the one racing the shipment.
        "blocklist": blocklist,
        "forwarder": ForwarderGuard(client=blocklist.client),
    }
    results, failed = {}, []
    for name, guard in guards.items():
        try:
            results[name] = guard.scan(
                processed_after=processed_after,
                dry_run=dry_run,
                max_pages=max_pages,
                active_only=active_only,
            )
        except Exception:
            logger.exception("%s guard failed", name)
            failed.append(name)
    if failed:
        raise RuntimeError(f"order guard(s) failed: {', '.join(failed)}")
    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run every lememe order guard.")
    parser.add_argument(
        "--since", help="Only scan orders processed on/after this date (YYYY-MM-DD)."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Tag / hold matches and notify (default: dry-run, read-only).",
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

    run_order_guards(
        processed_after=args.since,
        dry_run=not args.apply,
        max_pages=args.max_pages,
        active_only=not args.include_closed,
    )


if __name__ == "__main__":
    main()
