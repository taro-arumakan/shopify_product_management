"""Split a Meta Business Suite multi-brand Stories content export into one CSV per
brand and upload each to Google Drive.

Instagram Stories cannot be pulled retroactively via the Graph API (the API only
exposes the last 24h), but the Business Suite "Content" export retains the full
month with rich metrics (views, reach, likes, shares, profile visits, replies,
navigation, follows, sticker taps, link clicks). So the monthly flow is:
  1. In Business Suite, export Stories content for the month (all brands at once).
  2. Run this script on the downloaded CSV.

It keys rows by "Account ID" (= each brand's Instagram user id, looked up from the
brand client), writes "Instagram stories - <from> - <to>.csv" per brand preserving
the native columns, and uploads to MONTHLY_EXTRACTION_FOLDER_ID/<YYYYMM>/<brand>/
Instagram/. The reporting month and date range are derived from the file's data.

    uv run brands/scripts/split_instagram_stories.py ~/Downloads/May-01-2026_May-31-2026_xxxx.csv
"""

import csv
import datetime
import logging
import os
import sys
import tempfile

import utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
for noisy in ("googleapiclient", "urllib3", "google"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

BRANDS = ["Apricot Studios", "BLOSSOM", "Archivépke", "LEMEME", "ROH SEOUL", "SSIL"]


def parse_publish_date(value):
    # Business Suite "Publish time" looks like "05/20/2026 22:00"
    return datetime.datetime.strptime(value, "%m/%d/%Y %H:%M").date()


def main():
    if len(sys.argv) < 2:
        raise SystemExit(
            "usage: split_instagram_stories.py <business_suite_export.csv>"
        )
    src = os.path.expanduser(sys.argv[1])

    clients = {b: utils.client(b) for b in BRANDS}
    id_to_brand = {clients[b].ig_user_id: b for b in BRANDS}
    drive = clients[BRANDS[0]]

    with open(src, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames
        rows = list(reader)

    non_story = {r["Post type"] for r in rows} - {"IG story"}
    if non_story:
        logging.warning(f"file contains non-story post types: {non_story}")

    dates = [
        parse_publish_date(r["Publish time"]) for r in rows if r.get("Publish time")
    ]
    date_from, date_to = min(dates), max(dates)
    period = f"{date_from:%Y%m}"
    out_name = f"Instagram stories - {date_from:%Y-%m-%d} - {date_to:%Y-%m-%d}.csv"
    logging.info(
        f"{len(rows)} stories spanning {date_from}..{date_to} -> period {period}"
    )

    by_brand = {b: [] for b in BRANDS}
    skipped = {}
    for r in rows:
        brand = id_to_brand.get(r["Account ID"])
        if brand:
            by_brand[brand].append(r)
        else:
            skipped[r["Account ID"]] = r.get("Account name")

    tmp = tempfile.mkdtemp()
    for brand, brand_rows in by_brand.items():
        path = os.path.join(tmp, out_name)
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows(brand_rows)
        folder = drive._find_or_create_folder_path(
            drive.MONTHLY_EXTRACTION_FOLDER_ID, period, brand, "Instagram"
        )
        drive.replace_or_upload_to_drive(path, "text/csv", folder)
        os.remove(path)
        logging.info(
            f"  {brand}: {len(brand_rows)} stories -> {period}/{brand}/Instagram"
        )

    if skipped:
        logging.info(f"skipped non-target accounts: {skipped}")


if __name__ == "__main__":
    main()
