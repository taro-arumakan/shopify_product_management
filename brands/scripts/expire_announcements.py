"""Hide announcement bar messages once they expire.

Holiday notices (年末年始 / 韓国旧正月 / GW / お盆 / 秋夕) go up on every Korean
brand a few times a year and then have to come down again. Left up, they are
worse than useless: a banner saying shipping is paused when it is not.

Each entry in EXPIRIES names a message block and the JST date it should stop
being visible. On or after that date this sets `disabled: true` on the block.
Adding the next holiday means adding a row here.

It reads the live theme through the Admin API and writes the one file back,
rather than pushing a checked-out theme: `current_theme()` resolves whatever is
published at the moment the job runs, so a theme published since the notice went
up is still handled, and nothing outside sections/header-group.json is touched.
Merchants edit these themes daily, so writing anything wider would revert work.

Hiding the last visible message is safe — the sections guard on
`section.blocks.size > 0` and Shopify drops disabled blocks from `section.blocks`,
so the bar disappears rather than rendering an empty strip. The section is
deliberately left enabled, so the next notice only needs a block.

Idempotent: a block that is already hidden is skipped and the file is not
rewritten, so a double-fire or a re-run costs nothing.

    PYTHONPATH=. uv run brands/scripts/expire_announcements.py            # dry run
    PYTHONPATH=. uv run brands/scripts/expire_announcements.py --apply
    PYTHONPATH=. uv run brands/scripts/expire_announcements.py --apply --today 2026-10-01
"""

import datetime
import json
import logging
import re
import sys
from zoneinfo import ZoneInfo

import utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
for noisy in ("googleapiclient", "urllib3", "google"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

JST = ZoneInfo("Asia/Tokyo")
THEME_FILE = "sections/header-group.json"

KOREAN_BRANDS = [
    "ssil",
    "rohseoul",
    "lememe",
    "kume",
    "blossomhcompany",
    "apricotstudios",
]

EXPIRIES = [
    {
        "note": "CEC-509 Chuseok shipping notice",
        "block_id": "message_chuseok2026",
        # Shipping resumes on 9/28, but CATAL expect the backlog to delay
        # orders placed from the 28th too, so the notice stays up for as long as
        # that is true: through Saturday 10/3, hidden on Sunday 10/4.
        "hide_on_or_after": "2026-10-04",
        "brands": KOREAN_BRANDS,
    },
]


def due_entries(brand, today):
    return [
        e
        for e in EXPIRIES
        if brand in e["brands"]
        and today >= datetime.date.fromisoformat(e["hide_on_or_after"])
    ]


def split_banner(content):
    """Keep Shopify's auto-generated /* ... */ header so the file round-trips."""
    match = re.match(r"(\s*/\*.*?\*/\s*)", content, re.S)
    banner = match.group(1) if match else ""
    return banner, content[len(banner) :]


def expire_brand(brand, today, apply_changes):
    client = utils.client(brand)
    entries = due_entries(brand, today)
    if not entries:
        logger.info(f"{brand}: nothing due")
        return

    theme = client.current_theme()
    files = [
        f
        for f in client.theme_file_by_theme_name_and_file_name(
            theme["name"], THEME_FILE
        )
        if f["filename"] == THEME_FILE
    ]
    if len(files) != 1:
        raise RuntimeError(f"{brand}: expected one {THEME_FILE}, got {len(files)}")

    banner, body = split_banner(files[0]["body"]["content"])
    doc = json.loads(body)
    section = next(
        s for s in doc["sections"].values() if s.get("type") == "announcement-bar"
    )

    hidden = []
    for entry in entries:
        block = section.get("blocks", {}).get(entry["block_id"])
        if block is None:
            # Already deleted by hand, or the id changed in the theme editor.
            # Worth saying out loud rather than passing silently as a no-op.
            logger.warning(
                f"{brand}: no block {entry['block_id']} ({entry['note']}) — nothing to hide"
            )
            continue
        if block.get("disabled"):
            continue
        block["disabled"] = True
        hidden.append(entry["block_id"])

    if not hidden:
        logger.info(f"{brand}: already up to date on theme {theme['name']!r}")
        return

    still_visible = [
        b for b in section["block_order"] if not section["blocks"][b].get("disabled")
    ]
    logger.info(
        f"{brand}: hiding {hidden} on theme {theme['name']!r}; "
        f"{len(still_visible)} message(s) left visible"
    )
    if not apply_changes:
        return

    content = banner + json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    client.upsert_theme_file(theme["id"], THEME_FILE, content)
    logger.info(f"{brand}: written")


def main(argv):
    apply_changes = "--apply" in argv
    today = datetime.datetime.now(JST).date()
    if "--today" in argv:
        today = datetime.date.fromisoformat(argv[argv.index("--today") + 1])

    logger.info(f"today (JST) = {today}, apply = {apply_changes}")
    failures = []
    for brand in KOREAN_BRANDS:
        try:
            expire_brand(brand, today, apply_changes)
        except Exception:
            # One broken store must not stop the other five from being cleaned up.
            logger.exception(f"{brand}: failed")
            failures.append(brand)

    if failures:
        raise SystemExit(f"failed for: {', '.join(failures)}")


if __name__ == "__main__":
    main(sys.argv[1:])
