# Monthly report — data file specifications

A reference for the Claude session that drafts each brand's monthly client report.
Read this first, then read the brand's CSVs. It explains the Google Drive layout,
the fixed reporting methodology, and exactly what every file/column means and which
report section it feeds.

The pipeline auto-populates **Shopify, Meta, Instagram (except stories)**. Stories
and LINE are added by hand. All figures are JPY unless noted.

---

## 1. Drive layout

```
Monthly Extraction / <YYYYMM> / <brand> /
    Shopify/      ← auto (Shopify Admin → Analytics, 14 report cards)
    Meta/         ← auto (Meta Ad Manager, ad-level insights)
    Instagram/    ← auto except stories (account metrics, posts, format counts)
    GA/           ← auto (Google Analytics 4 — channel engagement, device)
    LINE/         ← manual (friends + broadcast exports)
    Monthly KPI rollup - <range>.csv   ← auto (the cross-source summary — start here)
```

Each source folder holds, per report, **two granularities**:
- a **13-month monthly** series ending in the report month (year-over-year + 12-month trend)
- a **daily** series for the report month only (to trace the latest month / build daily charts)

> **New in June 2026 onward** (May's report had to work around these — it now has them):
> real 12-month / 6-month trends, Meta spend **history** (not just the current month),
> **daily** Shopify sales & sessions, absolute IG **follower count**, blended **CAC**,
> discount-dependency, and **spend/ROAS by Meta objective**. June 2026 is also the
> **first month with true YoY** (the brands launched ~June 2025).

---

## 2. Fixed methodology (keep identical every month)

These definitions are brand-wide policy. Pin them in the prompt so numbers stay
comparable month to month:

| Metric | Definition |
|---|---|
| 売上 (Revenue) | **net_sales + shipping_charges** (税抜) |
| AOV (客単価) | based on **total_sales (税込)** ÷ orders |
| ROAS | **CV-objective ads only** — the `OFFSITE_CONVERSIONS` row of *Meta spend by objective* (exclude reach / profile-visit / traffic from the denominator) |
| 送料無料閾値 | ¥15,000 (context for AOV / checkout-completion reading) |
| 月商目標 | ¥2.0M (net_sales + shipping) — per brand, confirm each month |

Never invent missing data. If a field is absent, say so (as the May report did).

---

## 3. Shopify/  (folder: `Shopify/`)

Fourteen reports, each written as two CSVs: `<Report name> - <range>.csv`
(13-month monthly) and `<Report name> - daily - <range>.csv` (report month) —
28 files in all. Headers are Shopify's own display names. Key ones:

| File | Columns (key) | Feeds report section |
|---|---|---|
| **Total sales over time** | orders, gross_sales, discounts, returns, **net_sales**, **shipping_charges**, taxes, total_sales | Revenue (売上 = net_sales+shipping), monthly trend |
| **Average order value over time** | gross_sales, discounts, orders, average_order_value | AOV |
| **Sessions over time** | online_store_visitors, sessions | Funnel (top), sessions trend |
| **Conversion rate over time** / **breakdown** | sessions, sessions_with_cart_additions, sessions_that_reached_checkout, sessions_that_completed_checkout, conversion_rate | Funnel decomposition (カート→到達→完了), CVR |
| **New and returning customers (over time)** | customers, orders, total_sales BY new_or_returning_customer | 顧客構造 (new vs repeat), repeat rate |
| **Total sales by product** | product_title, net_items_sold, net_sales, … | 商品分析 (top products, concentration) |
| **Total sales by referrer** | order_referrer_source/name, orders, total_sales | 売上のチャネル別 (last-click) |
| **Sales attributed to marketing** | referring_channel/medium, orders, total_sales | チャネル寄与 |
| **Sessions by referrer** | referrer_source/name, session_city, sessions | 参照元構成 (social/direct/search) |
| **Sessions by landing page** | landing_page_path, sessions, conversion_rate | ランディングページ別の流入と転換（施策/コレクションページの効果） |
| **Conversion by channel** | referring_channel, sessions, conversion_rate | チャネル別CVR（IGの「量」と「転換の質」の対比） |
| **Sales by discount** | discount_name, net_sales, orders, discounts | 割引コード別の売上・利用（プロモ／送料無料CPの効果） |

The **daily** variants are what enable a daily sales / sessions chart (May had to
substitute daily IG reach because daily Shopify wasn't available — now it is).

> **Sales by discount** note: rows with a blank `discount_name` are non-discounted
> orders (usually the bulk of sales). Shipping discounts (e.g. 送料無料) show under
> their own name but may carry ¥0 `net_sales`/`discounts` since they reduce shipping,
> not item price — read them as "orders that used the code", not item-discount value.

---

## 4. Meta/  (folder: `Meta/`)

| File | Granularity | Key columns |
|---|---|---|
| **Meta ads by ad - <range>.csv** | 13-month monthly | report_start/end, campaign_name, adset_name, ad_name, **objective**, **optimization_goal**, spend (JPY), impressions, reach, frequency, link_clicks, ctr, cpc, cpm, add_to_cart, initiate_checkout, **purchases**, **purchase_value**, purchase_roas_meta, **roas_computed** |
| **Meta ads by ad - daily - <range>.csv** | report month daily | same, per day |
| **Meta spend by objective - <range>.csv** | 13-month monthly | month, **optimization_goal**, spend, purchases, purchase_value, roas_computed |
| **Meta spend by placement - <range>.csv** | 13-month monthly | month, publisher_platform (instagram/facebook/…), spend, purchases, purchase_value, roas_computed |
| **Meta ad set budgets - <month>.csv** | report-month snapshot | month, adset_id, adset_name, campaign_name, effective_status, budget_level (adset/campaign), daily_budget, lifetime_budget, **report_month_spend** |

- **Currency**: spend, values & budgets already converted to JPY (handles KRW accounts).
- **Budget is a current snapshot**, not historical — use it for planned-vs-actual in
  the report month (`daily_budget`/`lifetime_budget` vs `report_month_spend`); older
  months' budgets aren't recoverable from the API. `budget_level` says whether the
  budget is set at the ad set (ABO) or parent campaign (CBO).
- **roas_computed** = purchase_value / spend.
- **ROAS (CV-only)** = the `OFFSITE_CONVERSIONS` row of *Meta spend by objective*.
  Goals map to the report's split: `OFFSITE_CONVERSIONS` → CV(購入), `REACH` → リーチ,
  `PROFILE_VISIT` → プロフィール訪問, `LINK_CLICKS`/`LANDING_PAGE_VIEWS` → トラフィック.
- *Meta spend by placement* separates Instagram from incidental Facebook spillover.

---

## 5. Instagram/  (folder: `Instagram/`)

| File | Key columns | Feeds |
|---|---|---|
| **Instagram account metrics - <range>.csv** | month, reach, views, profile_views, website_clicks, total_interactions, follows (net), **followers_count** (absolute) | IG monthly table, 12-month trend |
| **Instagram account metrics - daily - <range>.csv** | date + same | **Daily IG reach chart** |
| **Instagram posts - <range>.csv** | post_id, timestamp, media_product_type (FEED/REELS), permalink, caption, reach, views, likes, comments, shares, saved, total_interactions | Top posts / content performance |
| **Instagram published format counts - <month>.csv** | month, feed_posts, reels, posts_total | 投稿本数 (feed/reels) |
| **Instagram stories - <range>.csv** | *(manual — Business Suite "Content / Stories" export, split per brand; **Japanese headers**)* | ストーリーズ本数・実績 |

- `reach` here is a near-month **deduplicated** total (built from ≤20-day windows).
  Note: the manual Business Suite per-metric export (and the May report, ~1.54M)
  used the **sum of daily reach**, which over-counts. Prefer this deduplicated
  monthly figure and stay consistent; the daily file is available if a summed
  number is needed to reconcile with old reports.
- `follows` = net follower change, derived from the daily `followers_count` series
  (month-over-month / day-over-day deltas), so it's not bound by the API's 30-day
  limit; it fills from when daily capture began (~June 2026). `followers_count` =
  absolute audience size (daily snapshot).
- Stories count is **not** in the API files — take it (and per-story metrics) from the
  manual stories CSV. Posts total here (= feed + reels) matches Business Suite's
  「トップコンテンツフォーマット → 投稿」; stories = that file's 「ストーリーズ」.

### ストーリーズCSVの列（日本語・Business Suite エクスポート）

手動のストーリーズCSVは Business Suite の日本語列名をそのまま保持します
（reporter_bundle が各ブランドに分割）。主な列:

| 列名 | 意味 |
|---|---|
| 投稿ID | ストーリーズID |
| アカウントID | IGアカウントID（ブランド振り分けに使用） |
| 説明 | キャプション |
| 公開時間 | 公開日時（`MM/DD/YYYY HH:MM`） |
| リンク | パーマリンク |
| 投稿タイプ | 種別（`Instagramストーリーズ`） |
| ビュー / リーチ | 閲覧数 / リーチ |
| いいね！の数 / シェア数 / 返信 | いいね / シェア / 返信 |
| フォロー数 / プロフィールへのアクセス | フォロー / プロフィール訪問 |
| ナビゲーション / スタンプのタップ / リンククリック | ナビゲーション / スタンプタップ / リンククリック |

このファイルの**行数 = 当月のストーリーズ本数**。

---

## 6. GA/  (folder: `GA/`)

Google Analytics 4 (web), complementing Shopify with metrics it can't give —
chiefly **engagement quality** and a clean channel grouping. Each report is a
13-month monthly CSV + a report-month daily CSV. GA counts sessions slightly
differently from Shopify, so treat the two as corroborating, not identical.

| File | Dimensions | Metrics | Feeds |
|---|---|---|---|
| **GA acquisition by channel - <range>.csv** | month, sessionDefaultChannelGroup | sessions, totalUsers, newUsers, engagedSessions, **engagementRate**, **averageSessionDuration**, **keyEvents** | チャネル別の流入と「質」。**Paid Social（広告）と Organic Social（自然IG）を分離** |
| **GA engagement overview - <range>.csv** | month | sessions, totalUsers, newUsers, engagedSessions, engagementRate, averageSessionDuration, userEngagementDuration, screenPageViews, keyEvents | エンゲージメントの月次トレンド（headline） |
| **GA by device - <range>.csv** | month, deviceCategory | sessions, engagedSessions, engagementRate | デバイス別（mobile/desktop/tablet） |

- **`engagementRate`** = engaged sessions ÷ sessions (0–1); **`averageSessionDuration`**
  in seconds; **`keyEvents`** = GA conversions (key events).
- The channel view is the standout: it separates **Paid Social** (Meta ads) from
  **Organic Social** (organic IG), which Shopify lumps together — paid traffic
  typically shows much lower engagement than organic.
- `sessionDefaultChannelGroup` values: Direct, Organic Social, Paid Social,
  Organic Search, Paid Search, Referral, Email, Organic Shopping, Unassigned.
- Like the IG follower data, **history only goes back to property setup** (~the
  brand's launch); months before that are simply absent.

## 7. LINE/  (folder: `LINE/`, manual)

LINE's exports use **English** column names (download via Claude in Chrome).

| File | Columns | Feeds |
|---|---|---|
| **friend_overview_<range>.csv** (one row per day) | `date`, `contacts` (友だち数), `targetReaches` (有効リーチ), `blocks` (ブロック) | LINE friend growth, block trend |
| **message_broadcast_<range>.csv** (one row per broadcast) | `broadcastId`, `sentDate`, `cmsUrl`, `deliveredCount` (配信数), `open` (開封), `clickUU` (クリックUU), `videoStartUU`, `videoCompleteUU`, then per-bubble `1_imp`/`1_click`/… | 配信回数・配信数・開封・クリック |

- Open rate = `open` / `deliveredCount`; click rate = `clickUU` / `deliveredCount`.
- The `N_*` columns are per-message-bubble breakdowns (usually not needed for the report).

---

## 8. Monthly KPI rollup - <range>.csv  (start here)

One row per month (13 months), the cross-source summary:

`month, orders, net_sales, average_order_value, returning_customer_rate, sessions,
conversion_rate, new_customers, ad_spend, ad_purchase_value, ad_purchases, ad_roas,
ig_reach, ig_views, ig_profile_views, ig_website_clicks, ig_total_interactions,
ig_follows, ig_followers_count, cac`

- `cac` = ad_spend / new_customers (blended; blank when no new customers / no Meta).
- For discount/promo analysis use **Sales by discount** (§3) — item-discount value
  is small for these brands and free-shipping promos don't appear in `discounts`.
- `ad_roas` here is **all-objective** (spend includes reach/awareness). For the
  headline CV ROAS, use *Meta spend by objective* (`OFFSITE_CONVERSIONS`).
- This single file drives the **6-month KPI table** and **12-month trend** directly.

---

## 9. Known gaps / notes

- **損益分岐ROAS** — needs each brand's cost structure (原価率・受取率・運営費率),
  which is not in any file. Omit unless separately provided.
- **Stories & LINE** are manual; everything else is auto.
- **Promo context** (popups, new-product drops, free-shipping campaigns) is NOT in
  the data and is essential for interpreting the numbers — supply it in the prompt.
