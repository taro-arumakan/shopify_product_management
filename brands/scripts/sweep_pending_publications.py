"""Publish drops to the channels their scheduled launch had to leave behind.

Shopify honours `PublicationInput.publishDate` on the Online Store only — "Only
online store channels support future publishing" — so a scheduled launch can
publish the store and nothing else, or every channel goes live days early.
`publish_by_product_or_collection_id` therefore publishes the store alone and
tags the product `pending-channel-publish`. This drains that queue.

Run it on an interval. There is nothing to schedule per drop: the queue is the
tag, which lives in Shopify next to the thing it describes, so it cannot drift
out of sync with a scheduler and has no horizon a one-shot scheduler would
impose. A product whose launch has not happened is left queued, a product that
has reached every channel loses the tag, and a missed run is caught by the next
one.

Minute precision is not the point — Google, Meta and Shop ingest on their own
cadence, so a few minutes here disappears into their sync lag. What matters is
that it runs, and keeps running.

    PYTHONPATH=. uv run brands/scripts/sweep_pending_publications.py            # dry run
    PYTHONPATH=. uv run brands/scripts/sweep_pending_publications.py --apply
    PYTHONPATH=. uv run brands/scripts/sweep_pending_publications.py --apply --shop kume
"""

import logging
import sys

from helpers.publication_catch_up import sweep_pending_channel_publishes

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
for noisy in ("googleapiclient", "urllib3", "google"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Every shop whose products can be created with a scheduled launch. A shop with
# nothing queued costs one query, so it is cheaper to include one than to find
# out later that a drop sat waiting on a shop nobody added.
SHOPS = [
    "apricotstudios",
    "archivepke",
    "asheis",
    "blossom",
    "gbh",
    "kume",
    "lememe",
    "rohseoul",
    "ssil",
]


def main(argv):
    apply_changes = "--apply" in argv
    shops = SHOPS
    if "--shop" in argv:
        shops = [argv[argv.index("--shop") + 1]]

    logger.info(f"sweeping {len(shops)} shop(s), apply = {apply_changes}")
    totals = {"published": 0, "cleared": 0, "waiting": 0}
    failures = []

    for shop in shops:
        try:
            res = sweep_pending_channel_publishes(shop, dry_run=not apply_changes)
        except Exception:
            # One shop with a bad token must not strand the other eight; a drop
            # left unpublished is the failure this job exists to prevent.
            logger.exception(f"{shop}: failed")
            failures.append(shop)
            continue
        totals["published"] += len(res["published"])
        totals["cleared"] += len(res["cleared"])
        totals["waiting"] += len(res["waiting"])

    logger.info(
        f"sweep done: {totals['published']} published, {totals['cleared']} cleared, "
        f"{totals['waiting']} still waiting"
    )
    if failures:
        raise SystemExit(f"failed for: {', '.join(failures)}")


if __name__ == "__main__":
    main(sys.argv[1:])
