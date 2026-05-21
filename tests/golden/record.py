"""Record golden-master fixtures for ``to_product_inputs``.

Hits each manifested sheet **once** via the live Google APIs and writes a JSON
fixture containing the raw sheet rows, the lazily-populated drive-link cache, and
the resulting ``product_inputs``. The replay test then reconstructs the output
offline from these fixtures.

Usage (from repo root, with .env / Google credentials available):

    python -m tests.golden.record            # record every brand
    python -m tests.golden.record alvana gbh # record specific brands

Re-run this only when a sheet's schema/parsing behaviour intentionally changes;
the committed fixtures are the source of truth for the tests.
"""

import json
import pathlib
import sys

from helpers.google_api_interface.interface import GoogleApiInterface
from utils import credentials
from tests.golden.manifest import CASES, CASES_BY_BRAND

FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"


# Live Google attributes copied from a real GoogleApiInterface onto the brand
# client (which also carries the Shopify-side mixins, e.g. product_title_to_handle
# used by the handle_suffix path).
_GOOGLE_ATTRS = (
    "google_credential_path",
    "scopes",
    "credentials",
    "drive_service",
    "sheets_service",
    "slides_service",
    "gspread_client",
    "sheet_id",
    "drive_link_cache",
)


def record_case(case):
    cred = credentials(case.shop_name)
    gi = GoogleApiInterface(cred.google_credential_path, sheet_id=cred.google_sheet_id)
    gi.drive_link_cache = {}

    # Run on the real brand client (via __new__, skipping its network-heavy
    # __init__) so every inherited method is available; borrow the live Google
    # clients from gi.
    client = case.new_client()
    for attr in _GOOGLE_ATTRS:
        setattr(client, attr, getattr(gi, attr))

    # Fetch the raw rows once, then pin them so to_product_inputs reads the same
    # snapshot we persist (avoids a second network read / drift mid-record).
    rows = client.worksheet_rows(cred.google_sheet_id, case.sheet_name)
    client.worksheet_rows = lambda sheet_id, sheet_title, _rows=rows: _rows

    expected = client.to_product_inputs(
        cred.google_sheet_id,
        case.sheet_name,
        case.start_row,
        product_attr_column_map=client.product_attr_column_map(),
        option1_attr_column_map=client.option1_attr_column_map(),
        option2_attr_column_map=client.option2_attr_column_map(),
        handle_suffix=case.handle_suffix,
    )

    fixture = {
        "brand": case.brand,
        "shop_name": case.shop_name,
        "sheet_name": case.sheet_name,
        "start_row": case.start_row,
        "handle_suffix": case.handle_suffix,
        "rows": rows,
        # row_num -> drive link; JSON keys must be strings, restored to int on load.
        "drive_link_cache": {str(k): v for k, v in client.drive_link_cache.items()},
        "expected": expected,
    }

    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIXTURES_DIR / f"{case.brand}.json"
    out_path.write_text(
        json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"[{case.brand}] recorded {len(rows)} rows -> "
        f"{len(expected)} products at {out_path}"
    )


def main(argv):
    brands = argv or [case.brand for case in CASES]
    failures = []
    for brand in brands:
        case = CASES_BY_BRAND.get(brand)
        if case is None:
            print(f"[{brand}] unknown brand; skipping")
            continue
        try:
            record_case(case)
        except Exception as exc:  # keep going so one stale sheet doesn't block the rest
            failures.append((brand, exc))
            print(f"[{brand}] FAILED: {type(exc).__name__}: {exc}")
    if failures:
        print(f"\n{len(failures)} brand(s) failed: {[b for b, _ in failures]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
