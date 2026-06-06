"""Extract the seed CSVs for the staff's monthly brand reports and upload them to
Google Drive. Covers Shopify Admin -> Analytics, Meta (Ad Manager) ad insights, and
Instagram (Business Suite) account/post metrics, plus a cross-source KPI rollup.

For each brand and report month this writes, per source:
  * a 13-month series (same month last year .. report month) for year-over-year
  * a daily series for the report month, so the latest month can be traced

Files land in Drive under Reporting.MONTHLY_EXTRACTION_FOLDER_ID as
<YYYYMM>/<brand>/{Shopify,Meta,Instagram}/<report>.csv, with the combined
<YYYYMM>/<brand>/Monthly KPI rollup - ....csv alongside them. Re-runs overwrite
same-named files. Meta/Instagram are skipped for brands without Meta creds.

Usage:
    python extract_monthly_reports.py                 # default brands, last full month
    python extract_monthly_reports.py apricot 2026 5  # one brand, explicit month
"""

import datetime
import logging
import sys

import utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
for noisy in ("googleapiclient", "urllib3", "google"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

DEFAULT_BRANDS = [
    "apricot",
    "blossom",
    "archivepke",
    "lememe",
    "roh",
    "ssil",
]


def last_full_month(today=None):
    today = today or datetime.date.today()
    first_of_this_month = today.replace(day=1)
    last_month_end = first_of_this_month - datetime.timedelta(days=1)
    return last_month_end.year, last_month_end.month


def main():
    args = sys.argv[1:]
    if args:
        brands = [args[0]]
        if len(args) >= 3:
            year, month = int(args[1]), int(args[2])
        else:
            year, month = last_full_month()
    else:
        brands = DEFAULT_BRANDS
        year, month = last_full_month()

    failures = []
    for brand in brands:
        logging.info(f"=== {brand} {year}-{month:02d} (Shopify + Meta + Instagram) ===")
        try:
            client = utils.client(brand)
            paths = client.extract_all_monthly(report_year=year, report_month=month)
            logging.info(
                f"{brand}: extracted sources "
                f"{sorted(k for k in paths if k != 'rollup')} + rollup"
            )
        except Exception as e:
            logging.exception(f"{brand} extraction failed: {e}")
            failures.append(brand)

    if failures:
        raise SystemExit(f"Monthly extraction failed for: {', '.join(failures)}")


if __name__ == "__main__":
    main()
