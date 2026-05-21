"""Golden-master tests for ``to_product_inputs`` (one canonical sheet per brand).

These lock in the *current* list-of-dicts output so the upcoming dict->class
refactor can be verified to preserve behaviour. Each test replays a recorded
sheet snapshot (see ``tests/golden/record.py``) entirely offline: the only
network entry points (``worksheet_rows`` and the drive-link cache) are stubbed,
and the parsing logic under test runs unchanged.

When the refactor lands, ``to_product_inputs`` will return ``Product`` instances
instead of dicts. At that point, update ``to_plain`` below to serialise them back
to dicts (e.g. ``[p.to_dict() for p in product_inputs]``); the recorded fixtures
stay the source of truth.
"""

import json
import pathlib

import pytest

from tests.golden.manifest import CASES

FIXTURES_DIR = pathlib.Path(__file__).parent / "golden" / "fixtures"


def to_plain(product_inputs):
    # Today to_product_inputs already returns plain dicts. After the dict->class
    # migration, convert instances back to dicts here so the assertion still
    # compares against the recorded fixtures.
    return product_inputs


def _load_fixture(brand):
    path = FIXTURES_DIR / f"{brand}.json"
    if not path.exists():
        pytest.skip(f"no fixture recorded for {brand} (run tests.golden.record)")
    return json.loads(path.read_text(encoding="utf-8"))


def _no_network(*args, **kwargs):
    raise AssertionError(
        "unexpected network call during golden replay; the drive-link cache "
        "should have been pre-populated from the fixture"
    )


@pytest.mark.parametrize("case", CASES, ids=[c.brand for c in CASES])
def test_to_product_inputs_matches_golden(case):
    fixture = _load_fixture(case.brand)

    client = case.new_client()
    client.product_sheet_start_row = fixture["start_row"]
    # Pre-seed the cache (keys are row numbers) so get_richtext_link never hits
    # the network, and make any populate attempt a loud failure.
    client.drive_link_cache = {
        int(k): v for k, v in fixture["drive_link_cache"].items()
    }
    client.populate_drive_link_cache = _no_network
    client.worksheet_rows = lambda sheet_id, sheet_title: fixture["rows"]

    result = client.to_product_inputs(
        "sheet-id-unused",
        fixture["sheet_name"],
        fixture["start_row"],
        product_attr_column_map=client.product_attr_column_map(),
        option1_attr_column_map=client.option1_attr_column_map(),
        option2_attr_column_map=client.option2_attr_column_map(),
        handle_suffix=fixture["handle_suffix"],
    )

    assert to_plain(result) == fixture["expected"]
