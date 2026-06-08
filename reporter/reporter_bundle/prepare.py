#!/usr/bin/env python3
"""Self-contained seed-prep helper for the monthly brand reports.

No repository, no credentials, no pip installs — Python standard library only.
Two commands:

  Split a Meta Business Suite "Stories" content export into one CSV per brand
  (writes to ./output/<YYYYMM>/<brand>/):
      python3 prepare.py stories "/path/to/StoriesExport.csv"

  Print the LINE export URLs for every brand for a given month (open each in the
  browser to download the CSV):
      python3 prepare.py line-urls 2026 06
"""

import calendar
import csv
import datetime
import os
import sys

# Instagram "Account ID" (from the Business Suite export) -> brand folder name.
IG_ACCOUNT_ID_TO_BRAND = {
    "17841466471650076": "Apricot Studios",
    "17841476193318947": "BLOSSOM",
    "17841468170371736": "Archivépke",
    "17841475715129638": "LEMEME",
    "17841466341118989": "ROH SEOUL",
    "17841407763844963": "SSIL",
}

# LINE Official Account ids (manager.line.biz) per brand.
LINE_ID_BY_BRAND = {
    "Apricot Studios": "@818uqsjw",
    "BLOSSOM": "@785vxvfi",
    "Archivépke": "@486sredm",
    "LEMEME": "@583kydkh",
    "ROH SEOUL": "@667zhxxw",
    "SSIL": "@106jxbdq",
}

JST_OFFSET = 9 * 3600  # Asia/Tokyo, no DST


# The Business Suite "Content / Stories" export uses the column language of the
# account it was downloaded from. Resolve the two columns we need in either
# Japanese or English. The values (Account ID = IG user id, Publish time =
# MM/DD/YYYY HH:MM) are identical across languages.
PUBLISH_TIME_COLUMNS = ("公開時間", "Publish time")
ACCOUNT_ID_COLUMNS = ("アカウントID", "Account ID")


def _resolve_column(fields, candidates):
    for c in candidates:
        if c in fields:
            return c
    raise SystemExit(
        f"Could not find any of {candidates} in the CSV columns: {list(fields)}"
    )


def split_stories(export_path):
    with open(export_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames
        rows = list(reader)

    publish_col = _resolve_column(fields, PUBLISH_TIME_COLUMNS)
    account_col = _resolve_column(fields, ACCOUNT_ID_COLUMNS)

    dates = [
        datetime.datetime.strptime(r[publish_col], "%m/%d/%Y %H:%M").date()
        for r in rows
        if r.get(publish_col)
    ]
    date_from, date_to = min(dates), max(dates)
    period = f"{date_from:%Y%m}"
    out_name = f"Instagram stories - {date_from:%Y-%m-%d} - {date_to:%Y-%m-%d}.csv"

    by_brand = {b: [] for b in IG_ACCOUNT_ID_TO_BRAND.values()}
    for r in rows:
        brand = IG_ACCOUNT_ID_TO_BRAND.get(r[account_col])
        if brand:
            by_brand[brand].append(r)

    print(f"{len(rows)} stories spanning {date_from}..{date_to}  (period {period})\n")
    for brand, brand_rows in by_brand.items():
        out_dir = os.path.join("output", period, brand)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, out_name)
        with open(out_path, "w", newline="", encoding="utf-8-sig") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows(brand_rows)
        print(f"  {brand:16} {len(brand_rows):>4} stories -> {out_path}")
    print(
        "\nNext: upload each output/<period>/<brand>/ file into the matching Drive "
        "folder  Monthly Extraction / <period> / <brand> / Instagram /"
    )


def line_urls(year, month):
    last = calendar.monthrange(year, month)[1]
    from_ts = calendar.timegm((year, month, 1, 0, 0, 0)) - JST_OFFSET
    to_ts = calendar.timegm((year, month, last, 23, 59, 59)) - JST_OFFSET
    ymd_from, ymd_to = f"{year}{month:02d}01", f"{year}{month:02d}{last:02d}"
    print(f"LINE export URLs for {year}-{month:02d}:\n")
    for brand, bid in LINE_ID_BY_BRAND.items():
        print(f"# {brand}")
        print(
            f"  friends:   https://manager.line.biz/api/bots/{bid}/insight/"
            f"contacts.csv?fromDate={ymd_from}&toDate={ymd_to}"
        )
        print(
            f"  broadcast: https://manager.line.biz/api/bots/{bid}/insight/"
            f"broadcastStats.csv?from={from_ts}&to={to_ts}\n"
        )
    print(
        "Open each URL in the browser (logged into LINE Manager) to download the CSV, "
        "then upload into  Monthly Extraction / "
        f"{year}{month:02d} / <brand> / LINE /"
    )


def main():
    args = sys.argv[1:]
    if len(args) >= 2 and args[0] == "stories":
        split_stories(os.path.expanduser(args[1]))
    elif len(args) >= 3 and args[0] == "line-urls":
        line_urls(int(args[1]), int(args[2]))
    else:
        print(__doc__)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
