"""Weekly favorites (wishlist) report for ASHEIS → Google Sheet.

Counts favorites from GA4, because guests never reach the backend at all (see
helpers/favorites_reporting.py for why), and uses Shopify only to resolve
names/stock and to verify that member favorites are still being persisted.

    uv run brands/scripts/favorites_weekly_report.py                 # last complete week
    uv run brands/scripts/favorites_weekly_report.py --weeks 4       # backfill 4 weeks
    uv run brands/scripts/favorites_weekly_report.py --include-current
    uv run brands/scripts/favorites_weekly_report.py --week 2026-09-14

Re-running a week is safe: rows are keyed on the week's Monday and replaced.
"""

import argparse
import datetime
import logging

import utils
from helpers.favorites_reporting import last_complete_week, week_bounds

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
for noisy in ("googleapiclient", "urllib3", "google"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

BRAND = "ASHEIS"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--week",
        type=lambda s: datetime.date.fromisoformat(s),
        help="any date inside the week to report (default: last complete week)",
    )
    parser.add_argument(
        "--weeks",
        type=int,
        default=1,
        help="number of consecutive weeks to write, counting back (default: 1)",
    )
    parser.add_argument(
        "--include-current",
        action="store_true",
        help="also write the in-progress week, marked 進行中",
    )
    return parser.parse_args()


def weeks_to_report(args):
    latest = week_bounds(args.week)[0] if args.week else last_complete_week()
    weeks = [latest - datetime.timedelta(days=7 * i) for i in range(args.weeks)]
    if args.include_current and not args.week:
        current = week_bounds(datetime.date.today())[0]
        if current not in weeks:
            weeks.insert(0, current)
    # Oldest first, so "前週比" can read the previous week's row once written.
    return sorted(weeks)


def main():
    args = parse_args()
    client = utils.client(BRAND)
    client.ensure_favorites_sheet()

    failures = []
    for week_start in weeks_to_report(args):
        logging.info(f"favorites week starting {week_start}")
        try:
            client.upsert_favorites_week(week_start)
        except Exception as e:
            logging.exception(f"favorites week {week_start} failed: {e}")
            failures.append(str(week_start))

    if failures:
        raise SystemExit(f"favorites weekly report failed for: {', '.join(failures)}")


if __name__ == "__main__":
    main()
