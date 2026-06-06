"""Daily capture of perishable Instagram data for every brand.

Instagram Stories vanish from the API after 24h and follows are only served for
the trailing 30 days, so this runs daily (via GitHub Actions) to accumulate the
history the monthly report needs. Per brand it stores, under
MONTHLY_EXTRACTION_FOLDER_ID/_daily/<brand>/Instagram/:
  * account/<date>.csv  - the day's account metrics (incl. follows)
  * stories/<date>.csv  - live stories + insights

Captures yesterday (JST) by default. Pass YYYY-MM-DD to capture a specific day
(only useful for stories still within their 24h window).

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
