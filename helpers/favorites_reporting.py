"""Weekly favorites (wishlist) reporting for ASHEIS.

The favorites feature is split across two systems, and the split is the whole
reason this report exists:

* a **logged-in** customer's heart click POSTs to the shopify_favorites_service
  Cloud Run app, which writes a customer metafield;
* a **guest**'s heart click never leaves the browser — it lives in
  localStorage only.

So Shopify's own data sees logged-in customers only, and has no idea how much
the feature is actually used. GA4 sees both, because the storefront publishes
every toggle to Shopify's customer-events bus and a custom web pixel forwards
it. Everything here therefore counts favorites from GA4 and uses Shopify only
to resolve names/stock and to check that member favorites are still persisting.

See ANALYTICS.md in the shopify_favorites_service repo for the full chain.
"""

import datetime
import json
import logging
import re
import time
import zoneinfo

import gspread

logger = logging.getLogger(__name__)

JST = zoneinfo.ZoneInfo("Asia/Tokyo")

# The GA4 property's own timezone is Asia/Tokyo, so its `date` dimension is
# already JST and week boundaries need no shifting.
FAVORITES_SHEET_ID = "1TYnXZ9l1piDCC_sMyNufRZ9zLtpXdQ9r3518RegpKmo"

TAB_SUMMARY = "週次サマリー"
TAB_ITEMS = "アイテム別"
TAB_GUIDE = "指標の説明"

ADD_EVENT = "add_to_wishlist"
REMOVE_EVENT = "remove_from_wishlist"

# Persistence-check states. "OK" is reserved for a check that actually ran:
# with no member activity there is nothing to verify, and saying OK would
# claim a green light nobody earned.
HEALTH_OK = "OK"
HEALTH_SUSPECT = "要確認"
HEALTH_NO_MEMBER = "会員利用なし"
HEALTH_UNKNOWN = "判定不可"

# The Google & YouTube channel reports ecommerce items as
# "shopify_ZZ_<productId>_<variantId>"; our own favorites carry the bare
# product id, so this is what joins favorites to views/carts/purchases.
ECOM_ITEM_ID = re.compile(r"^shopify_\w+_(\d+)_(\d+)$")

SUMMARY_HEADERS = [
    "週開始",
    "期間",
    "状態",
    "追加",
    "解除",
    "純増",
    "利用者数",
    "ゲスト追加",
    "会員追加",
    "ゲスト比率",
    "商品お気に入り",
    "記事お気に入り",
    "商品PV",
    "100PVあたり追加",
    "前週比",
    "トップ3",
    "会員保存件数",
    "保存整合",
    "更新日時",
]

ITEM_HEADERS = [
    "週開始",
    "種別",
    "ID",
    "名称",
    "追加数",
    "ゲスト",
    "会員",
    "閲覧数",
    "100閲覧あたり",
    "カート追加",
    "購入",
    "在庫",
    "シグナル",
    "更新日時",
]

TRANSIENT_SHEET_ERRORS = {429, 500, 502, 503, 504}


def week_bounds(any_date):
    """The ISO week (Mon–Sun) containing `any_date`, as (monday, sunday)."""
    monday = any_date - datetime.timedelta(days=any_date.weekday())
    return monday, monday + datetime.timedelta(days=6)


def last_complete_week(today=None):
    """Monday of the most recent week that has fully ended."""
    today = today or datetime.datetime.now(JST).date()
    this_monday, _ = week_bounds(today)
    return this_monday - datetime.timedelta(days=7)


class FavoritesReporting:
    # --- GA4 -------------------------------------------------------------

    def _fav_ga_report(self, dimensions, metrics, dimension_filter=None, limit=10000):
        """One GA4 report against this brand's property, with an optional filter.

        `ga_run_report` always prepends a time dimension and cannot filter, which
        is why this exists alongside it.
        """
        property_id = self.ga_property_id(self.BRAND_NAME)
        if not property_id:
            raise RuntimeError(f"no GA4 property mapped for {self.BRAND_NAME}")
        body = {
            "dateRanges": [
                {
                    "startDate": f"{self._fav_start:%Y-%m-%d}",
                    "endDate": f"{self._fav_end:%Y-%m-%d}",
                }
            ],
            "dimensions": [{"name": d} for d in dimensions],
            "metrics": [{"name": m} for m in metrics],
            "limit": limit,
        }
        if dimension_filter:
            body["dimensionFilter"] = dimension_filter
        res = (
            self.analytics_data_service.properties()
            .runReport(property=f"properties/{property_id}", body=body)
            .execute()
        )
        rows = []
        for r in res.get("rows", []):
            rows.append(
                (
                    [d["value"] for d in r["dimensionValues"]],
                    [m["value"] for m in r["metricValues"]],
                )
            )
        return rows

    @staticmethod
    def _event_filter(*event_names):
        if len(event_names) == 1:
            return {
                "filter": {
                    "fieldName": "eventName",
                    "stringFilter": {"value": event_names[0]},
                }
            }
        return {
            "filter": {
                "fieldName": "eventName",
                "inListFilter": {"values": list(event_names)},
            }
        }

    @staticmethod
    def _path_prefix_filter(prefix):
        return {
            "filter": {
                "fieldName": "pagePath",
                "stringFilter": {"matchType": "BEGINS_WITH", "value": prefix},
            }
        }

    # --- measures --------------------------------------------------------

    def _favorites_totals(self):
        """Adds/removes and distinct users, split guest vs member."""
        rows = self._fav_ga_report(
            ["eventName", "customEvent:logged_in"],
            ["eventCount", "totalUsers"],
            self._event_filter(ADD_EVENT, REMOVE_EVENT),
        )
        out = {
            "adds": 0,
            "removes": 0,
            "guest_adds": 0,
            "member_adds": 0,
            "member_removes": 0,
            "add_users": 0,
        }
        for (event, logged_in), (count, users) in rows:
            count, users = int(count), int(users)
            if event == ADD_EVENT:
                out["adds"] += count
                out["add_users"] += users
                if logged_in == "yes":
                    out["member_adds"] += count
                else:
                    out["guest_adds"] += count
            elif event == REMOVE_EVENT:
                out["removes"] += count
                if logged_in == "yes":
                    out["member_removes"] += count
        return out

    def _favorites_by_item(self):
        """add_to_wishlist per item id, split guest vs member.

        Rows collected before the pixel started sending `item_id` (2026-09-12)
        report "(not set)"; they still count in the totals but cannot be
        attributed to an item, so they are dropped here.
        """
        rows = self._fav_ga_report(
            ["customEvent:item_id", "customEvent:item_kind", "customEvent:logged_in"],
            ["eventCount"],
            self._event_filter(ADD_EVENT),
        )
        items = {}
        for (item_id, kind, logged_in), (count,) in rows:
            if item_id == "(not set)" or kind == "(not set)":
                continue
            entry = items.setdefault(
                (kind, item_id), {"guest": 0, "member": 0, "total": 0}
            )
            count = int(count)
            entry["member" if logged_in == "yes" else "guest"] += count
            entry["total"] += count
        return items

    def _page_views(self, prefix):
        rows = self._fav_ga_report(
            ["pagePath"], ["screenPageViews"], self._path_prefix_filter(prefix)
        )
        return {path: int(v) for (path,), (v,) in rows}

    def _item_commerce(self):
        """Views / cart-adds / purchases per Shopify product id."""
        rows = self._fav_ga_report(
            ["itemId"], ["itemsViewed", "itemsAddedToCart", "itemsPurchased"]
        )
        out = {}
        for (item_id,), (viewed, carted, bought) in rows:
            m = ECOM_ITEM_ID.match(item_id)
            if not m:
                continue
            entry = out.setdefault(m.group(1), {"viewed": 0, "carted": 0, "bought": 0})
            entry["viewed"] += int(viewed)
            entry["carted"] += int(carted)
            entry["bought"] += int(bought)
        return out

    # --- Shopify ---------------------------------------------------------

    def _resolve_items(self, keys):
        """(kind, id) -> title/handle/stock, via one Admin API call."""
        if not keys:
            return {}
        gids = [
            f"gid://shopify/{'Product' if kind == 'product' else 'Article'}/{item_id}"
            for kind, item_id in keys
        ]
        query = """
        query FavoriteTargets($ids: [ID!]!) {
            nodes(ids: $ids) {
                ... on Product { id handle title totalInventory status }
                ... on Article { id handle title }
            }
        }
        """
        res = self.run_query(query, {"ids": gids})
        return {n["id"]: n for n in res["nodes"] if n}

    def _stored_favorites_count(self):
        """Favorites actually persisted on customer metafields, counted item by item.

        Deliberately not `metafieldDefinitions.metafieldsCount`: that counts the
        customers who hold a metafield, not the favorites inside it. A returning
        member adding a second favorite would leave it unchanged, and the
        persistence check below would cry wolf.
        """
        query = """
        query StoredFavorites($cursor: String) {
            customers(first: 250, after: $cursor) {
                pageInfo { hasNextPage endCursor }
                nodes {
                    products: metafield(
                        namespace: "custom", key: "favorite_products"
                    ) { value }
                    articles: metafield(
                        namespace: "custom", key: "favorite_articles"
                    ) { value }
                }
            }
        }
        """
        total, cursor = 0, None
        while True:
            page = self.run_query(query, {"cursor": cursor})["customers"]
            for node in page["nodes"]:
                for key in ("products", "articles"):
                    total += self._gid_list_length((node.get(key) or {}).get("value"))
            if not page["pageInfo"]["hasNextPage"]:
                return total
            cursor = page["pageInfo"]["endCursor"]

    @staticmethod
    def _gid_list_length(raw):
        """list.* metafields store a JSON array of GIDs as their string value."""
        if not raw:
            return 0
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning(f"unparsable favorites metafield value: {raw!r}")
            return 0
        return len(value) if isinstance(value, list) else 0

    # --- assembling the rows ---------------------------------------------

    def favorites_week(self, week_start):
        """Every measure for one ISO week. Returns (summary_dict, item_rows)."""
        monday, sunday = week_bounds(week_start)
        today = datetime.datetime.now(JST).date()
        self._fav_start, self._fav_end = monday, min(sunday, today)

        totals = self._favorites_totals()
        items = self._favorites_by_item()
        product_views = self._page_views("/products/")
        article_views = self._page_views("/blogs/")
        commerce = self._item_commerce()
        resolved = self._resolve_items(items.keys())

        item_rows = []
        for (kind, item_id), counts in items.items():
            gid = (
                f"gid://shopify/{'Product' if kind == 'product' else 'Article'}"
                f"/{item_id}"
            )
            node = resolved.get(gid)
            title = node["title"] if node else f"(不明 {item_id})"
            if node and kind == "product":
                views = commerce.get(item_id, {}).get("viewed", 0) or product_views.get(
                    f"/products/{node['handle']}", 0
                )
            elif node:
                views = article_views.get(f"/blogs/styling/{node['handle']}", 0)
            else:
                views = 0
            c = commerce.get(item_id, {})
            stock = node.get("totalInventory") if node and kind == "product" else None
            item_rows.append(
                {
                    "kind": kind,
                    "id": item_id,
                    "title": title,
                    "total": counts["total"],
                    "guest": counts["guest"],
                    "member": counts["member"],
                    "views": views,
                    "rate": round(100 * counts["total"] / views, 1) if views else None,
                    "carted": c.get("carted", 0),
                    "bought": c.get("bought", 0),
                    "stock": stock,
                }
            )
        for row in item_rows:
            row["signal"] = self._item_signal(row)
        item_rows.sort(key=lambda r: (-r["total"], -(r["rate"] or 0)))

        product_pv = sum(product_views.values())
        summary = {
            "week_start": monday,
            "week_end": sunday,
            "partial": sunday >= today,
            "adds": totals["adds"],
            "removes": totals["removes"],
            "net": totals["adds"] - totals["removes"],
            "users": totals["add_users"],
            "guest_adds": totals["guest_adds"],
            "member_adds": totals["member_adds"],
            "guest_share": (
                round(100 * totals["guest_adds"] / totals["adds"], 1)
                if totals["adds"]
                else None
            ),
            "product_favs": sum(
                r["total"] for r in item_rows if r["kind"] == "product"
            ),
            "article_favs": sum(
                r["total"] for r in item_rows if r["kind"] == "article"
            ),
            "product_pv": product_pv,
            "per_100_pv": (
                round(100 * totals["adds"] / product_pv, 2) if product_pv else None
            ),
            "top3": "、".join(r["title"] for r in item_rows[:3]),
            "stored": self._stored_favorites_count(),
        }
        return summary, item_rows

    @staticmethod
    def _item_signal(row):
        """The one-line reason a merchandiser might care about this item."""
        signals = []
        if row["rate"] is not None and row["rate"] >= 5 and row["views"] < 100:
            signals.append("注目度高・露出不足")
        if row["total"] >= 2 and row["bought"] == 0:
            signals.append("未購入")
        if row["stock"] is not None and row["stock"] <= 15 and row["total"] >= 1:
            signals.append("在庫僅少")
        return "／".join(signals)

    # --- writing ---------------------------------------------------------

    def _with_sheet_retry(self, fn, *args, max_retries=5, **kwargs):
        """Sheets 5xx/429 are transient; a momentary outage must not fail the run."""
        for attempt in range(max_retries):
            try:
                return fn(*args, **kwargs)
            except gspread.exceptions.APIError as e:
                status = getattr(getattr(e, "response", None), "status_code", None)
                if attempt == max_retries - 1 or status not in TRANSIENT_SHEET_ERRORS:
                    raise
                wait = 3 * (attempt + 1)
                logger.warning(
                    f"Sheets transient error ({status}); retrying in {wait}s "
                    f"({attempt + 1}/{max_retries})"
                )
                time.sleep(wait)

    def upsert_favorites_week(self, week_start, sheet_id=FAVORITES_SHEET_ID):
        """Write one week's summary row and its item rows, replacing any existing."""
        summary, item_rows = self.favorites_week(week_start)
        # Tabs must exist before anything reads or writes them.
        spreadsheet = self.ensure_favorites_sheet(sheet_id)

        now = datetime.datetime.now(JST).strftime("%Y-%m-%d %H:%M")
        key = f"{summary['week_start']:%Y-%m-%d}"

        prev = self._previous_summary(spreadsheet, key)
        summary["wow"] = self._wow(summary["adds"], prev)
        summary["health"] = self._health(summary, prev, now)

        self._with_sheet_retry(self._upsert_summary, spreadsheet, summary, key, now)
        self._with_sheet_retry(
            self._replace_item_rows, spreadsheet, item_rows, key, now
        )
        logger.info(
            f"favorites week {key}: {summary['adds']} adds "
            f"({summary['guest_adds']} guest / {summary['member_adds']} member), "
            f"{len(item_rows)} items"
        )
        return summary, item_rows

    def _previous_summary(self, spreadsheet, key):
        ws = spreadsheet.worksheet(TAB_SUMMARY)
        values = ws.get_all_values()[1:]
        earlier = [r for r in values if r and r[0] and r[0] < key]
        return max(earlier, key=lambda r: r[0]) if earlier else None

    @staticmethod
    def _wow(adds, prev):
        if not prev:
            return None
        try:
            before = int(prev[3])
        except (ValueError, IndexError):
            return None
        if not before:
            return None
        return round(100 * (adds - before) / before, 1)

    @staticmethod
    def _health(summary, prev, now):
        """Whether member favorites demonstrably persisted this week.

        Members favoriting while the stored total does not grow means the write
        path is suspect -- exactly the failure that ran unnoticed for five weeks
        after launch.

        The stored total is a live reading, not history, so it can only be
        compared against a row written on an earlier day. Backfilling several
        weeks in one run gives every row the same reading, and a flat delta
        there says nothing at all.
        """
        if not summary["member_adds"]:
            return HEALTH_NO_MEMBER
        if prev is None:
            return HEALTH_UNKNOWN
        try:
            before = int(prev[16])
            written = prev[18][:10]
        except (ValueError, IndexError):
            return HEALTH_UNKNOWN
        if written == now[:10]:
            return HEALTH_UNKNOWN
        if summary["member_adds"] - summary["member_removes"] <= 0:
            # Adds cancelled out by removes, so a flat stored total is expected.
            return HEALTH_OK
        return HEALTH_OK if summary["stored"] > before else HEALTH_SUSPECT

    def _summary_row(self, s, now):
        return [
            f"{s['week_start']:%Y-%m-%d}",
            f"{s['week_start']:%m/%d} 〜 {s['week_end']:%m/%d}",
            "進行中" if s["partial"] else "確定",
            s["adds"],
            s["removes"],
            s["net"],
            s["users"],
            s["guest_adds"],
            s["member_adds"],
            "" if s["guest_share"] is None else s["guest_share"] / 100,
            s["product_favs"],
            s["article_favs"],
            s["product_pv"],
            "" if s["per_100_pv"] is None else s["per_100_pv"],
            "" if s.get("wow") is None else s["wow"] / 100,
            s["top3"],
            s["stored"],
            s["health"],
            now,
        ]

    def _upsert_summary(self, spreadsheet, summary, key, now):
        ws = spreadsheet.worksheet(TAB_SUMMARY)
        row = self._summary_row(summary, now)
        existing = [r[0] if r else "" for r in ws.get_all_values()]
        if key in existing[1:]:
            index = existing.index(key, 1) + 1
            ws.update(
                range_name=f"A{index}:S{index}",
                values=[row],
                value_input_option="USER_ENTERED",
            )
        else:
            ws.insert_row(row, index=2, value_input_option="USER_ENTERED")

    def _replace_item_rows(self, spreadsheet, item_rows, key, now):
        """Delete this week's item rows, then insert the fresh set under the header."""
        ws = spreadsheet.worksheet(TAB_ITEMS)
        values = ws.get_all_values()
        for i in range(len(values), 1, -1):
            if values[i - 1] and values[i - 1][0] == key:
                ws.delete_rows(i)
        rows = [
            [
                key,
                "商品" if r["kind"] == "product" else "記事",
                r["id"],
                r["title"],
                r["total"],
                r["guest"],
                r["member"],
                r["views"],
                "" if r["rate"] is None else r["rate"],
                r["carted"],
                r["bought"],
                "" if r["stock"] is None else r["stock"],
                r["signal"],
                now,
            ]
            for r in item_rows
        ]
        if rows:
            ws.insert_rows(rows, row=2, value_input_option="USER_ENTERED")

    # --- sheet setup -----------------------------------------------------

    def ensure_favorites_sheet(self, sheet_id=FAVORITES_SHEET_ID):
        """Create and style the three tabs. Safe to re-run; headers are rewritten."""
        spreadsheet = self.gspread_client.open_by_key(sheet_id)
        existing = {ws.title: ws for ws in spreadsheet.worksheets()}

        # A brand-new sheet arrives as a single default tab; reuse it rather
        # than leaving an empty "Sheet1" behind.
        default = existing.get("Sheet1") or existing.get("シート1")
        if default and TAB_SUMMARY not in existing:
            default.update_title(TAB_SUMMARY)
            existing[TAB_SUMMARY] = default

        specs = [
            (TAB_SUMMARY, SUMMARY_HEADERS),
            (TAB_ITEMS, ITEM_HEADERS),
            (TAB_GUIDE, None),
        ]
        for title, headers in specs:
            if title not in existing:
                cols = len(headers) if headers else 3
                existing[title] = spreadsheet.add_worksheet(
                    title=title, rows=1000, cols=cols
                )

        self._write_headers(existing[TAB_SUMMARY], SUMMARY_HEADERS)
        self._write_headers(existing[TAB_ITEMS], ITEM_HEADERS)
        self._write_guide(existing[TAB_GUIDE])

        requests = []
        requests += self._header_style_requests(
            existing[TAB_SUMMARY].id, len(SUMMARY_HEADERS)
        )
        requests += self._header_style_requests(
            existing[TAB_ITEMS].id, len(ITEM_HEADERS)
        )
        requests += self._summary_format_requests(existing[TAB_SUMMARY].id)
        requests += self._items_format_requests(existing[TAB_ITEMS].id)
        requests += self._guide_style_requests(existing[TAB_GUIDE].id)
        self.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id, body={"requests": requests}
        ).execute()
        return spreadsheet

    @staticmethod
    def _write_headers(worksheet, headers):
        worksheet.update(
            range_name=f"A1:{gspread.utils.rowcol_to_a1(1, len(headers))}",
            values=[headers],
        )

    @staticmethod
    def _header_style_requests(tab_id, width):
        return [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": tab_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": width,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 0.12,
                                "green": 0.13,
                                "blue": 0.15,
                            },
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE",
                            "wrapStrategy": "WRAP",
                            "textFormat": {
                                "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                                "bold": True,
                                "fontSize": 10,
                            },
                        }
                    },
                    "fields": "userEnteredFormat",
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": tab_id,
                        "gridProperties": {"frozenRowCount": 1},
                    },
                    "fields": "gridProperties.frozenRowCount",
                }
            },
            {
                "setBasicFilter": {
                    "filter": {
                        "range": {
                            "sheetId": tab_id,
                            "startRowIndex": 0,
                            "startColumnIndex": 0,
                            "endColumnIndex": width,
                        }
                    }
                }
            },
        ]

    @staticmethod
    def _number_format(tab_id, start_col, end_col, pattern, kind="NUMBER"):
        return {
            "repeatCell": {
                "range": {
                    "sheetId": tab_id,
                    "startRowIndex": 1,
                    "startColumnIndex": start_col,
                    "endColumnIndex": end_col,
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {"type": kind, "pattern": pattern}
                    }
                },
                "fields": "userEnteredFormat.numberFormat",
            }
        }

    @staticmethod
    def _column_width(tab_id, start_col, end_col, pixels):
        return {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": tab_id,
                    "dimension": "COLUMNS",
                    "startIndex": start_col,
                    "endIndex": end_col,
                },
                "properties": {"pixelSize": pixels},
                "fields": "pixelSize",
            }
        }

    def _summary_format_requests(self, tab_id):
        return [
            self._number_format(tab_id, 9, 10, "0.0%", "PERCENT"),  # ゲスト比率
            self._number_format(tab_id, 14, 15, "+0.0%;-0.0%", "PERCENT"),  # 前週比
            self._number_format(tab_id, 13, 14, "0.00"),  # 100PVあたり
            self._column_width(tab_id, 0, 1, 95),
            self._column_width(tab_id, 1, 2, 110),
            self._column_width(tab_id, 15, 16, 300),  # トップ3
            self._column_width(tab_id, 18, 19, 130),
        ]

    def _items_format_requests(self, tab_id):
        return [
            self._number_format(tab_id, 8, 9, "0.0"),  # 100閲覧あたり
            self._column_width(tab_id, 0, 1, 95),
            self._column_width(tab_id, 2, 3, 130),
            self._column_width(tab_id, 3, 4, 260),  # 名称
            self._column_width(tab_id, 12, 13, 200),  # シグナル
            self._column_width(tab_id, 13, 14, 130),
        ]

    def _guide_style_requests(self, tab_id):
        return [
            self._column_width(tab_id, 0, 1, 190),
            self._column_width(tab_id, 1, 2, 560),
            self._column_width(tab_id, 2, 3, 380),
            {
                "repeatCell": {
                    "range": {"sheetId": tab_id, "startRowIndex": 0, "endRowIndex": 1},
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 0.12,
                                "green": 0.13,
                                "blue": 0.15,
                            },
                            "textFormat": {
                                "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                                "bold": True,
                            },
                        }
                    },
                    "fields": "userEnteredFormat",
                }
            },
            {
                "repeatCell": {
                    "range": {"sheetId": tab_id, "startRowIndex": 1},
                    "cell": {
                        "userEnteredFormat": {
                            "wrapStrategy": "WRAP",
                            "verticalAlignment": "TOP",
                        }
                    },
                    "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)",
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": tab_id,
                        "gridProperties": {"frozenRowCount": 1},
                    },
                    "fields": "gridProperties.frozenRowCount",
                }
            },
        ]

    def _write_guide(self, worksheet):
        rows = GUIDE_ROWS
        worksheet.clear()
        worksheet.update(range_name=f"A1:C{len(rows)}", values=rows)


GUIDE_ROWS = [
    ["項目", "意味", "読み方・打ち手"],
    [
        "■ このレポートについて",
        "",
        "",
    ],
    [
        "計測の前提",
        "お気に入り機能は、ログイン中のお客様がハートを押した場合のみサーバー"
        "（Cloud Run）に送信され、Shopifyの顧客メタフィールドに保存されます。"
        "未ログインのお客様（ゲスト）の場合はブラウザのlocalStorageにのみ保存され、"
        "サーバーには一切送信されません。",
        "したがってShopify側の数字は「会員のみ」を表します。"
        "Shopifyの保存件数が少ないことは「使われていない」ことを意味しません。"
        "全体の利用状況はGA4でのみ把握できます。",
    ],
    [
        "数字の精度",
        "GA4はgoogletagmanager.comを読み込むため、広告ブロッカーを使っている"
        "訪問者は計測されません。一方サーバーへの送信は自社ドメイン経由のため"
        "ブロックされません。",
        "ゲストの数値は実態の下限値です。ゲスト比率は表示値より高い可能性が"
        "あります。件数そのものより「率」や「順位」の方が信頼できます。",
    ],
    [
        "アイテム別の開始時期",
        "アイテム単位の集計は、ピクセルがitem_idを送り始めた2026年9月12日以降の"
        "データのみ対象です。それ以前のお気に入りは週次サマリーの合計には"
        "含まれますが、どの商品かは特定できません。",
        "2026-09-07の週だけ、サマリーの追加数とアイテム別の合計が一致しません。"
        "翌週以降は一致します。",
    ],
    ["", "", ""],
    ["■ 週次サマリー", "", ""],
    ["週開始 / 期間", "対象週（月曜〜日曜）。", "—"],
    [
        "状態",
        "確定＝週が終了済み。進行中＝集計時点でまだ週の途中。",
        "「進行中」の行は翌週に自動で上書きされ「確定」になります。",
    ],
    [
        "追加 / 解除 / 純増",
        "お気に入りに追加された数、解除された数、その差。",
        "純増が継続的にマイナスなら、期待と中身がずれている可能性。",
    ],
    [
        "利用者数",
        "お気に入りを追加した人数（重複を除く）。",
        "件数より人数の伸びの方が、機能の定着を表します。",
    ],
    [
        "ゲスト追加 / 会員追加 / ゲスト比率",
        "未ログイン・ログイン済みそれぞれの追加数と、ゲストの占める割合。",
        "ゲスト比率が高い＝購買意欲を示しているのに誰か分からないお客様が多い"
        "状態。ログイン誘導や会員登録特典の価値を測る指標です。",
    ],
    [
        "商品お気に入り / 記事お気に入り",
        "商品ページとスタイリング記事、それぞれの追加数。",
        "記事が多いなら、コンテンツが接点として機能しています。",
    ],
    ["商品PV", "対象週の商品ページ閲覧数の合計。", "次の指標の分母です。"],
    [
        "100PVあたり追加",
        "商品ページ100回の閲覧あたり、何件お気に入りされたか。",
        "流入量の影響を除いた「機能の使われ方」。"
        "アクセスが少ない週でも、この値が保たれていれば機能自体は健全です。",
    ],
    ["前週比", "追加数の前週からの増減率。", "—"],
    [
        "トップ3",
        "その週で最も多くお気に入りされた3件。",
        "詳細は「アイテム別」タブを参照。",
    ],
    [
        "会員保存件数",
        "Shopifyの顧客メタフィールドに保存されているお気に入りの総件数（全顧客の合計）。"
        "ゲストのお気に入りはブラウザ内にしか存在しないため含まれません。",
        "会員が1件追加すればこの数も1増えるはずです。次の「保存整合」の判定材料です。",
    ],
    [
        "保存整合",
        "会員のお気に入りが実際に保存されたかの判定。4つの状態があります。\n"
        "OK＝会員の追加が記録され、保存件数も増えた。\n"
        "要確認＝会員の追加が記録されたのに保存件数が増えていない。\n"
        "会員利用なし＝その週は会員による追加がなく、確認する対象がなかった。\n"
        "判定不可＝比較できる前週の記録がない、または前週分と同じ日にまとめて"
        "書き込まれたため差分が意味を持たない。",
        "「要確認」が出たら保存処理が壊れている可能性があります。"
        "実際に公開直後の約5週間、保存が全く機能しておらず気づけませんでした。"
        "この欄はその再発を検知するためのものです。\n"
        "「会員利用なし」は異常ではありませんが、正常だと確認できたわけでもありません。"
        "現在ほぼ全てのお気に入りがゲストによるものため、この状態が続くのが通常です。",
    ],
    ["", "", ""],
    ["■ アイテム別", "", ""],
    [
        "追加数 / ゲスト / 会員",
        "その週にお気に入りされた回数と内訳。",
        "順位＝いま欲しがられているもの。",
    ],
    ["閲覧数", "その商品・記事の閲覧数。", "—"],
    [
        "100閲覧あたり",
        "見た人のうち、どれくらいの割合がお気に入りしたか。",
        "この値が高く閲覧数が少ない商品は「刺さっているのに見られていない」"
        "状態。特集・コレクション追加・メール/SNSでの露出が有効です。",
    ],
    [
        "カート追加 / 購入",
        "同じ週の、その商品のカート追加数と購入数。",
        "お気に入りは多いのに購入が0なら、価格・サイズ欠品・後押し不足を疑います。",
    ],
    [
        "在庫",
        "現在の在庫数（商品のみ）。",
        "お気に入りが多く在庫が少ないものは、再入荷または在庫僅少の訴求を検討。",
    ],
    [
        "シグナル",
        "上記の組み合わせから自動で付く注意ラベル。"
        "「注目度高・露出不足」「未購入」「在庫僅少」。",
        "打ち手を考える起点として、まずここが付いた行を見てください。",
    ],
]
