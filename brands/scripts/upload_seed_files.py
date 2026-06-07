"""Upload local seed CSVs to a brand's monthly-extraction folder in Google Drive.

Generic helper for manual/interim seed files (e.g. LINE exports downloaded via the
browser). Uploads each file to
MONTHLY_EXTRACTION_FOLDER_ID/<period>/<brand>/<category>/, overwriting same-named
files (idempotent).

    uv run brands/scripts/upload_seed_files.py 202606 "ROH SEOUL" LINE \
        ~/Downloads/friend_overview_20260601_20260630.csv \
        ~/Downloads/message_broadcast_20260601_20260630.csv
"""

import logging
import os
import sys

import utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
for noisy in ("googleapiclient", "urllib3", "google"):
    logging.getLogger(noisy).setLevel(logging.WARNING)


def main():
    if len(sys.argv) < 5:
        raise SystemExit(
            "usage: upload_seed_files.py <YYYYMM> <brand> <category> <file...>"
        )
    period, brand, category = sys.argv[1], sys.argv[2], sys.argv[3]
    files = [os.path.expanduser(p) for p in sys.argv[4:]]

    client = utils.client(brand)
    folder = client._find_or_create_folder_path(
        client.MONTHLY_EXTRACTION_FOLDER_ID, period, brand, category
    )
    for path in files:
        if not os.path.exists(path):
            logging.warning(f"missing, skipped: {path}")
            continue
        client.replace_or_upload_to_drive(path, "text/csv", folder)
        logging.info(
            f"uploaded {os.path.basename(path)} -> {period}/{brand}/{category}"
        )


if __name__ == "__main__":
    main()
