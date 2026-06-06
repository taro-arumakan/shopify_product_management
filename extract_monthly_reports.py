"""Extract the seed CSVs for the staff's monthly brand reports and upload them to
Google Drive. Covers Shopify Admin -> Analytics and Meta (Ad Manager) ad insights.

For each brand and report month this writes, per source:
  * a 13-month series (same month last year .. report month) for year-over-year
  * a daily series for the report month, so the latest month can be traced

Files land in Drive under Reporting.MONTHLY_EXTRACTION_FOLDER_ID as
<YYYYMM>/<brand>/Shopify/<report>.csv and <YYYYMM>/<brand>/Meta/<report>.csv.
Re-runs overwrite same-named files. Meta is skipped for brands without Meta creds.

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

    for brand in brands:
        client = utils.client(brand)

        logging.info(f"=== Shopify: {brand} {year}-{month:02d} ===")
        client.extract_shopify_analytics_reports(report_year=year, report_month=month)

        if client.meta_ad_account_id and client.meta_token:
            logging.info(f"=== Meta: {brand} {year}-{month:02d} ===")
            client.extract_meta_ads_reports(report_year=year, report_month=month)
        else:
            logging.info(f"=== Meta: skipped for {brand} (no Meta credentials) ===")


if __name__ == "__main__":
    main()
