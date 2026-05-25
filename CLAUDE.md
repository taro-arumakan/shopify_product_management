# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A collection of Python scripts that automate Shopify store management for ~10 different brand storefronts (alvana, apricotstudios, archivepke, blossom, gbh, kume, lememe, rohseoul, ssil, leisureallstars, plus a `dev` quickstart store). Source-of-truth for product catalogs lives in **per-brand Google Sheets**; scripts read those sheets, fetch images from Google Drive, and create/update products via the **Shopify Admin GraphQL API** (`2025-10`). There is no web service — everything is invoked as one-off scripts locally or via GitHub Actions `workflow_dispatch`.

## Tooling / common commands

- Package manager: **uv** (Python `>=3.13`, dependencies pinned in `uv.lock`). Install: `uv sync`.
- Run any script: `uv run path/to/script.py` (the script needs `PYTHONPATH=.` so imports like `from utils import ...` resolve — VSCode `launch.json` and the GitHub workflows set this).
- Tests: `uv run pytest` (see `pytest.ini`; `testpaths = tests`). Single test: `uv run pytest tests/test_utils.py::TestUtils::test_client_kume`.
- Formatter / hooks: `uv run pre-commit run --all-files` (black 25.1.0, trailing-whitespace, end-of-file-fixer, **and pytest runs as a pre-commit hook on every commit touching `.py`** — do not bypass with `--no-verify`).
- Re-record golden fixtures (requires real credentials + network): `uv run python -m tests.golden.record` — only do this when sheet structure intentionally changes.

## Credentials & environment

All scripts read a local `.env` (see `utils.credentials`). Required keys follow a `{SHOPNAME}-ACCESS_TOKEN` / `{SHOPNAME}-GSPREAD_ID` naming convention, plus `GOOGLE_CREDENTIAL_PATH` pointing at a Google service-account JSON. `SHOPNAME` is the actual Shopify subdomain (`kumej`, `blossomhcompany`, `apricot-studios`, `archive-epke`, `quickstart-6f3c9e4c` for dev, …), **not** the human brand name — `utils.client()` maps friendly aliases (`"kume"`, `"blossom"`, `"dev"`, etc.) to the right `SHOPNAME` and instantiates the matching brand client. Always go through `utils.client(...)` rather than constructing a client by hand. `install.py` is a one-off OAuth helper for minting a new `shpat_...` access token.

## Architecture — the big picture

Three layers of mixin-based composition. Understanding this is the only way to navigate the codebase:

1. **`helpers/shopify_graphql_client/`** — one file per Shopify domain (`product_create.py`, `inventory.py`, `medias.py`, `collections.py`, `orders.py`, `metafields.py`, `publications.py`, `merge_products_as_variants.py`, …). Each defines a class with related queries/mutations. They're all mixed into `ShopifyGraphqlClient` (`helpers/shopify_graphql_client/client.py`), which owns `run_query` / `run_paginated_query` and the `base_url`. **When you need a new Shopify operation, add a method to the relevant mixin file rather than creating a new class** — the existing inheritance chain will pick it up automatically.

2. **`helpers/client.Client`** — multiply inherits `ShopifyGraphqlClient`, `GoogleApiInterface` (Drive + Sheets + Slides via gspread + google-api-python-client), `Reporting`, and `MetaReportingInterface`. Methods here orchestrate across services — e.g. `process_product_images` reads from Drive, uploads to Shopify, and assigns the new media to variants. This layer is brand-agnostic.

3. **`brands/<brand>/client.py`** — each brand subclasses `BrandClientBase` (`brands/client/brandclientbase.py`, which itself extends `Client` + `SanityChecks`). A brand client only needs to declare `SHOPNAME` / `VENDOR` / `LOCATIONS` and implement a handful of overrides: `product_attr_column_map`, `option1_attr_column_map`, `option2_attr_column_map` (mapping Google Sheet column letters to product fields), `get_description_html`, and `get_size_field`. The entry point that ties it all together is `BrandClientBase.process_sheet_to_products(sheet_name=...)`: read sheet → build `product_inputs` (list of dicts) → run sanity checks → create products → upload images → set inventory → publish (optionally `scheduled_time`). Some brands have multiple variants of their client (e.g. `BlossomClientShoes`, `GbhClientSizeOptionOnly`) for catalog subsets with different option schemas.

The top-level `*.py` scripts (`publish_products.py`, `inventory_set_quantity.py`, `product_tags_update.py`, …) and `brands/<brand>/*.py` are all thin entry points that call `utils.client(<alias>).<method>()`.

### product_input shape

The core data structure passed everywhere. Built by `to_product_inputs` (in the Sheets helper) from a brand's column maps. Example:
```python
{"title": ..., "handle": ..., "price": ..., "options": [
    {"option_values": {"カラー": "PINK", "サイズ": "2"}, "sku": "...", "stock": 2, "drive_link": "..."},
    ...
]}
```
`segment_options_list_by_key_option` groups variants by the first option (typically color) — this is how multi-color/multi-size products map to per-color image folders on Drive.

## Conventions to follow

- **Don't add backwards-compat shims for brand-client APIs** — there are many brands, but each script imports its brand client directly, so renames are safe (just grep first).
- **Sheet column maps use `string.ascii_lowercase.index("d")`** for readability against the spreadsheet — keep that style when editing column maps; don't replace with magic numbers.
- **Brand client overrides raise `NotImplementedError`** for things every brand must implement (`product_attr_column_map`, `get_description_html`, `get_size_field`). If a brand truly doesn't need one, override with a `pass` or sensible default rather than leaving it unimplemented.
- **Japanese / non-ASCII** column names (`カラー`, `サイズ`) and brand aliases (`archivépke`, `kumé`) are intentional and load-bearing — preserve them exactly.
- **GraphQL IDs**: pass either a numeric ID or a `gid://shopify/...` string; `ShopifyGraphqlClient.sanitize_id(identifier, prefix=...)` normalizes both. Use it instead of hand-formatting gids.
- **Pagination**: any query taking `$first: Int!` with `pageInfo { hasNextPage endCursor }` should be invoked via `run_paginated_query(query, variables, data_key)`, not a hand-rolled loop.
- **Logging**: every module uses `logger = logging.getLogger(__name__)`. Entry-point scripts call `logging.basicConfig(level=logging.INFO)` in `main()` — keep that pattern.
- **`brands/scripts/`** holds cross-brand batch jobs (monthly reports, dashboard updates, expired-order cleanup) wired to scheduled GitHub Actions in `.github/workflows/`. **`deprecated/`** is dead code kept for reference; don't import from it. **`playground/`** is for ad-hoc experiments.

## Tests

- `tests/test_product_inputs_golden.py` is a **golden-master** suite that replays recorded sheet rows through each brand's column-map parsing, fully offline (network calls are stubbed to assert-fail). When you change column maps or `to_product_inputs`, expect a diff in `tests/golden/fixtures/<brand>.json` — review the diff carefully, then re-record via `python -m tests.golden.record` if the change is intentional. Adding a brand means adding a `GoldenCase` to `tests/golden/manifest.py` and re-recording.
- `tests/test_client_helpers.py` covers pure helpers on `Client` (option grouping, size-text → HTML table). Construct test instances with `Client.__new__(Client)` to skip network-touching `__init__`.

## GitHub Actions

`.github/workflows/run_func.yml` and `run_script.yml` let any script/function be triggered from the Actions UI with `workflow_dispatch`. They build `.env` from repo secrets, install via `uv sync --frozen`, then execute. The other workflows (monthly reports, dashboard, expired orders, abandoned-cart tagging) are scheduled cron jobs that call into `brands/scripts/` or `.github/actions/`.
