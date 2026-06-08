# Reporter assets

Source-controlled copies of the materials handed to the (non-technical) monthly
brand-report reporter. These otherwise only live on disk (`~/`) and in Google
Drive; this directory is their backup / source of truth for the disk artifacts.

The monthly process has two phases.

## Phase 1 — seed preparation: `reporter_bundle/`

What the reporter's Claude Cowork runs each month to prepare the seed files the
pipeline can't auto-fetch (IG stories, LINE):

- `prepare.py` — stdlib-only helper. Splits the Meta Business Suite "Content /
  Stories" export into one CSV per brand (handles Japanese **or** English headers)
  and prints the per-brand LINE export URLs.
- `毎月の作業プロンプト.txt` — the monthly Cowork prompt (Phase 1 only).
- `はじめにお読みください.md` — reporter-facing readme.

Distributed by zipping this folder → Google Drive `_reporter_bundle`.

## Phase 2 — report generation: `report_generation_kit/`

Reference materials for the **separate** session that writes the monthly report
from the seed CSVs. The two reference docs are maintained canonically in `docs/`:

- [`docs/monthly_report_file_specs.md`](../docs/monthly_report_file_specs.md) —
  data dictionary (also kept at the Drive Monthly-Extraction root).
- [`docs/monthly_report_prompt_JA.md`](../docs/monthly_report_prompt_JA.md) —
  sample drafting prompt to adapt.

`report_generation_kit/はじめにお読みください.md` is the reporter-facing readme. The
distributed kit (Drive `_report_generation_kit`) bundles those two `docs/` files
**plus** this readme together — so when `docs/` changes, re-sync the Drive copies.

> The pipeline never reads this directory. The two MDs are **not** duplicated here
> on purpose — `docs/` is their single source of truth.
