"""Daily snapshot of each brand's absolute Instagram follower count.

followers_count is a live field the Graph API can't backfill, so this runs once
daily (via GitHub Actions) to accumulate the end-of-month figures / audience
curve the monthly report overlays. Per brand it stores, under
MONTHLY_EXTRACTION_FOLDER_ID/_daily/<brand>/Instagram/account/<date>.csv, then
refreshes the combined account.csv. (Account metrics like reach/views are
re-fetched by the monthly run, and stories come from the manual Business Suite
export, so neither is captured here.)

Captures yesterday (JST) by default. Pass YYYY-MM-DD to capture a specific day.

    uv run brands/scripts/capture_instagram_daily.py
    uv run brands/scripts/capture_instagram_daily.py 2026-06-05
"""

import datetime
import logging
import sys

import utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
for noisy in ("googleapiclient", "urllib3", "google"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

BRANDS = [
    "Apricot Studios",
    "BLOSSOM",
    "Archivépke",
    "LEMEME",
    "ROH SEOUL",
    "SSIL",
]


def main():
    capture_date = None
    if len(sys.argv) > 1 and sys.argv[1].strip():
        capture_date = datetime.date.fromisoformat(sys.argv[1].strip())

    failures = []
    for brand in BRANDS:
        client = utils.client(brand)
        if not (client.ig_user_id and client.meta_token):
            logging.info(f"skip {brand}: no Instagram credentials")
            continue
        try:
            client.capture_instagram_daily(capture_date=capture_date)
            client.combine_ig_daily_files()
        except Exception as e:
            logging.exception(f"{brand} daily capture failed: {e}")
            failures.append(brand)

    if failures:
        raise SystemExit(f"Instagram daily capture failed for: {', '.join(failures)}")


if __name__ == "__main__":
    main()
