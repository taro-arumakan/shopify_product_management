import datetime
import logging
import time
import pandas as pd
import requests
import zoneinfo


logger = logging.getLogger(__name__)


class MetaReportingInterface:
    # Paid reporting covers ALL placements so the headline reconciles with the
    # money actually spent (the account bills across placements regardless of
    # intent). A publisher_platform breakdown surfaces the per-placement split
    # (e.g. Facebook spillover at ~0 ROAS). Set to ("instagram",) to hard-filter.
    PUBLISHER_PLATFORMS = None

    def __init__(self, fb_page_id, ig_user_id, meta_ad_account_id, meta_token):
        self.VERSION = "v25.0"
        self.fb_page_id = fb_page_id
        self.ig_user_id = ig_user_id
        self.meta_ad_account_id = meta_ad_account_id
        self.meta_token = meta_token

    def _publisher_platform_filtering(self):
        """Insights ``filtering`` param restricting to PUBLISHER_PLATFORMS, or None."""
        if not self.PUBLISHER_PLATFORMS:
            return None
        platforms = list(self.PUBLISHER_PLATFORMS)
        return f"[{{'field':'publisher_platform','operator':'IN','value':{platforms}}}]"

    omni_ig_keys = [
        "views",
        "reach",
        "saves",
        "profile_views",
        "website_clicks",
        "total_interactions",
    ]

    # The six Business Suite "結果" (Results) account metrics. The Graph API only
    # serves these as a single total_value per call (no daily breakdown), but a
    # 1-day window returns that day's value exactly, so iterating days rebuilds the
    # daily series Business Suite shows. 'follows' is special-cased: follower_count
    # is the only follows metric and the API serves it for the last 30 days only.
    IG_ACCOUNT_METRICS = [
        "reach",
        "views",
        "profile_views",
        "website_clicks",
        "total_interactions",
    ]

    def ig_account_metrics_for_day(self, day):
        """The day's account metrics as a flat dict (one 1-day total_value call).

        Includes 'follows' (follower_count) only when the day is within the API's
        trailing-30-day window; otherwise the column is left blank.
        """
        url = f"https://graph.facebook.com/{self.VERSION}/{self.ig_user_id}/insights"
        since = int(datetime.datetime(day.year, day.month, day.day).timestamp())
        until = int(
            (
                datetime.datetime(day.year, day.month, day.day)
                + datetime.timedelta(days=1)
            ).timestamp()
        )
        res = self._meta_get_with_retry(
            url,
            {
                "metric": ",".join(self.IG_ACCOUNT_METRICS),
                "period": "day",
                "metric_type": "total_value",
                "since": since,
                "until": until,
                "access_token": self.meta_token,
            },
        )
        row = {"date": f"{day:%Y-%m-%d}"}
        for metric in res.get("data", []):
            row[metric["name"]] = metric.get("total_value", {}).get("value")

        if datetime.date.today() - day <= datetime.timedelta(days=30):
            follows = self._meta_get_with_retry(
                url,
                {
                    "metric": "follower_count",
                    "period": "day",
                    "since": since,
                    "until": until,
                    "access_token": self.meta_token,
                },
            )
            values = (follows.get("data") or [{}])[0].get("values") or []
            row["follows"] = sum(v.get("value", 0) for v in values) if values else None
        else:
            row["follows"] = None
        return row

    def ig_account_metrics_by_day(self, date_from, date_to):
        """Daily account-metric rows for an inclusive date range (one call per day)."""
        rows = []
        day = date_from
        while day <= date_to:
            rows.append(self.ig_account_metrics_for_day(day))
            day += datetime.timedelta(days=1)
        logger.info(
            f"{self.__class__.__name__} pulled IG account metrics for "
            f"{len(rows)} days ({date_from} .. {date_to})"
        )
        return rows

    # Story-level insight metrics (image & video stories support these).
    IG_STORY_METRICS = [
        "reach",
        "views",
        "replies",
        "navigation",
        "profile_visits",
        "profile_activity",
        "follows",
        "shares",
        "total_interactions",
    ]

    def ig_stories_with_insights(self):
        """Currently-live stories (last 24h) with their insights, one row each.

        Instagram only exposes stories for 24h, so this must run daily to accumulate
        history — past stories cannot be fetched retroactively.
        """
        url = f"https://graph.facebook.com/{self.VERSION}/{self.ig_user_id}/stories"
        listing = self._meta_get_with_retry(
            url,
            {
                "fields": "id,media_type,media_product_type,timestamp,permalink,caption",
                "access_token": self.meta_token,
            },
        )
        rows = []
        for story in listing.get("data", []):
            row = {
                "story_id": story.get("id"),
                "timestamp": story.get("timestamp"),
                "media_type": story.get("media_type"),
                "media_product_type": story.get("media_product_type"),
                "permalink": story.get("permalink"),
                "caption": story.get("caption"),
            }
            try:
                insights = self._meta_get_with_retry(
                    f"https://graph.facebook.com/{self.VERSION}/{story['id']}/insights",
                    {
                        "metric": ",".join(self.IG_STORY_METRICS),
                        "access_token": self.meta_token,
                    },
                )
                for metric in insights.get("data", []):
                    values = metric.get("values")
                    row[metric["name"]] = (
                        values[0]["value"]
                        if values
                        else metric.get("total_value", {}).get("value")
                    )
            except RuntimeError as e:
                logger.warning(
                    f"{self.__class__.__name__} story {story.get('id')} insights "
                    f"unavailable: {e}"
                )
            rows.append(row)
        logger.info(f"{self.__class__.__name__} captured {len(rows)} live stories")
        return rows

    # Per-post insight metrics differ by media product type: Reels don't support
    # follows / profile_visits / profile_activity.
    IG_POST_METRICS = {
        "FEED": [
            "reach",
            "views",
            "likes",
            "comments",
            "shares",
            "saved",
            "total_interactions",
            "follows",
            "profile_visits",
            "profile_activity",
        ],
        "REELS": [
            "reach",
            "views",
            "likes",
            "comments",
            "shares",
            "saved",
            "total_interactions",
        ],
    }
    IG_MEDIA_FIELDS = (
        "id,caption,media_type,media_product_type,permalink,timestamp,"
        "like_count,comments_count"
    )

    def ig_media_list(self, date_from, date_to):
        """Published posts (FEED/REELS) with timestamps in an inclusive date range."""
        url = f"https://graph.facebook.com/{self.VERSION}/{self.ig_user_id}/media"
        params = {
            "fields": self.IG_MEDIA_FIELDS,
            "since": int(
                datetime.datetime(
                    date_from.year, date_from.month, date_from.day
                ).timestamp()
            ),
            "until": int(
                (
                    datetime.datetime(date_to.year, date_to.month, date_to.day)
                    + datetime.timedelta(days=1)
                ).timestamp()
            ),
            "limit": 100,
            "access_token": self.meta_token,
        }
        items = []
        while url:
            res = self._meta_get_with_retry(url, params)
            items.extend(res["data"])
            url = res.get("paging", {}).get("next")
            params = None
        # the since/until media filter is approximate; pin strictly to the range
        return [
            m
            for m in items
            if date_from <= datetime.date.fromisoformat(m["timestamp"][:10]) <= date_to
        ]

    def ig_posts_with_insights(self, date_from, date_to):
        """Posts published in the range, each with its insights, one flat row each."""
        media = self.ig_media_list(date_from, date_to)
        rows = []
        for m in media:
            ptype = m.get("media_product_type")
            row = {
                "post_id": m.get("id"),
                "timestamp": m.get("timestamp"),
                "media_type": m.get("media_type"),
                "media_product_type": ptype,
                "permalink": m.get("permalink"),
                "caption": m.get("caption"),
                "like_count": m.get("like_count"),
                "comments_count": m.get("comments_count"),
            }
            metrics = self.IG_POST_METRICS.get(ptype, self.IG_POST_METRICS["REELS"])
            try:
                insights = self._meta_get_with_retry(
                    f"https://graph.facebook.com/{self.VERSION}/{m['id']}/insights",
                    {"metric": ",".join(metrics), "access_token": self.meta_token},
                )
                for metric in insights.get("data", []):
                    values = metric.get("values")
                    row[metric["name"]] = (
                        values[0]["value"]
                        if values
                        else metric.get("total_value", {}).get("value")
                    )
            except RuntimeError as e:
                logger.warning(
                    f"{self.__class__.__name__} post {m.get('id')} insights "
                    f"unavailable: {e}"
                )
            rows.append(row)
        logger.info(
            f"{self.__class__.__name__} pulled {len(rows)} posts with insights "
            f"({date_from} .. {date_to})"
        )
        return rows

    def ig_published_format_counts(self, date_from, date_to):
        """Count of published posts by product type (the 'posts' half of 概要's
        トップコンテンツフォーマット; the stories count comes from daily capture)."""
        media = self.ig_media_list(date_from, date_to)
        counts = {"FEED": 0, "REELS": 0}
        for m in media:
            ptype = m.get("media_product_type")
            counts[ptype] = counts.get(ptype, 0) + 1
        return counts

    @staticmethod
    def aggregate_ig_metrics_by_month(daily_rows):
        """Sum daily account-metric rows into monthly totals (YYYY-MM-01 keyed)."""
        metrics = [
            "reach",
            "views",
            "profile_views",
            "website_clicks",
            "total_interactions",
            "follows",
        ]
        months = {}
        for row in daily_rows:
            month = row["date"][:7] + "-01"
            bucket = months.setdefault(month, {"month": month})
            for m in metrics:
                value = row.get(m)
                if value is not None:
                    bucket[m] = bucket.get(m, 0) + int(value)
        return [months[k] for k in sorted(months)]

    def _get_omni_ig_stat_value_by_key(self, d, k):
        return [dd for dd in d if dd["name"] == k][0]["total_value"]["value"]

    def _omni_ig_stats(self, start_date, end_date):
        logger.info(f"omni IG stats between {start_date} and {end_date}")

        acc_url = (
            f"https://graph.facebook.com/{self.VERSION}/{self.ig_user_id}/insights"
        )
        acc_res = requests.get(
            acc_url,
            params={
                "metric": "views,reach,profile_views,website_clicks,saves,total_interactions",
                "metric_type": "total_value",
                "period": "day",
                "since": int(start_date.timestamp()),
                "until": int(end_date.timestamp()),
                "access_token": self.meta_token,
            },
        )

        acc_data = acc_res.json()["data"]
        return {
            k: self._get_omni_ig_stat_value_by_key(acc_data, k)
            for k in self.omni_ig_keys
        }

    def omni_ig_stats(self, start_date, end_date):
        # XXX Facebook Graph API limitation for Instagram - only 30 days limitation
        delta = end_date - start_date
        MAX_RANGE = datetime.timedelta(days=30)

        if delta > MAX_RANGE:
            mid_point = start_date + MAX_RANGE
            ranges = [(start_date, mid_point), (mid_point, end_date)]
        else:
            ranges = [(start_date, end_date)]

        total_stats = {}
        for s, e in ranges:
            period_res = self._omni_ig_stats(s, e)
            for k in self.omni_ig_keys:
                total_stats.setdefault(k, 0)
                total_stats[k] += period_res[k]
        return total_stats

    def _sum_fb_metric(self, data, metric_name):
        """Helper to sum daily values from FB Page Insights"""
        for item in data:
            if item["name"] == metric_name:
                return sum(v["value"] for v in item["values"])

    def omni_fb_stats(self, start_date, end_date):
        # 1. Exchange the System User Token for a Page Access Token
        token_url = f"https://graph.facebook.com/{self.VERSION}/{self.fb_page_id}"
        token_res = requests.get(
            token_url,
            params={"fields": "access_token", "access_token": self.meta_token},
        ).json()
        page_access_token = token_res["access_token"]

        # 2. Fetch Facebook Page Stats
        fb_metrics_map = {
            "page_media_view": "views",  # Total Impressions equivalent
            "page_total_media_view_unique": "reach",  # Total Reach equivalent
            "page_views_total": "profile_views",  # Profile Views
            # "page_post_engagements": "total_interactions",  # Total Clicks/Actions
        }

        fb_url = f"https://graph.facebook.com/{self.VERSION}/{self.fb_page_id}/insights"
        fb_res = requests.get(
            fb_url,
            params={
                "metric": ",".join(fb_metrics_map.keys()),
                "period": "day",
                "metrics_type": "total_value",
                "since": int(start_date.timestamp()),
                "until": int(end_date.timestamp()),
                "access_token": page_access_token,
            },
        ).json()

        fb_raw = fb_res["data"]
        return {v: self._sum_fb_metric(fb_raw, k) for k, v in fb_metrics_map.items()}

    def omni_stats(self, start_date, end_date):
        logger.info(f"omni stats between {start_date} and {end_date}")
        ig_data = self.omni_ig_stats(start_date=start_date, end_date=end_date)
        fb_data = self.omni_fb_stats(start_date=start_date, end_date=end_date)
        return {
            k: ig_data[k] + fb_data.get(k, 0)
            for k in [
                "views",
                "reach",
                "profile_views",
                "saves",
                # "website_clicks",
                # "total_interactions",
            ]
        }

    def get_historical_exchange_rate(self, rate_date, from_curr, to_curr="JPY"):
        if isinstance(rate_date, datetime.date):
            rate_date = f"{rate_date:%Y-%m-%d}"
        url = f"https://api.frankfurter.dev/v2/rate/{from_curr}/{to_curr}?date={rate_date}"
        res = requests.get(url).json()
        return res["rate"]

    exchange_rates_by_date_by_pair = {}

    def jpy_rate(self, currency, rate_date):
        """Cached <currency>->JPY rate for a date (1.0 when already JPY)."""
        if not currency or currency == "JPY":
            return 1.0
        pair = f"{currency}JPY"
        if not self.exchange_rates_by_date_by_pair.get(rate_date, {}).get(pair):
            rate = self.get_historical_exchange_rate(rate_date, currency)
            self.exchange_rates_by_date_by_pair.setdefault(rate_date, {})[pair] = rate
        return self.exchange_rates_by_date_by_pair[rate_date][pair]

    def apply_exchange_rate(self, res):
        rate = self.jpy_rate(res.get("account_currency"), res.get("date_stop"))
        if rate != 1.0:
            res["spend"] = round(float(res["spend"]) * rate)
        return res

    def paid_stats(self, start_date: datetime.datetime, end_date: datetime.datetime):
        logger.info(f"paid stats between {start_date} and {end_date}")
        url = f"https://graph.facebook.com/{self.VERSION}/act_{self.meta_ad_account_id}/insights"

        # Note: Marketing API uses 'YYYY-MM-DD' strings for time_range,
        # unlike the IG API which uses Unix timestamps.

        params = {
            "level": "account",
            "fields": "account_currency,impressions,reach,inline_link_clicks,outbound_clicks,spend",
            "time_range": f"{{'since':'{start_date:%Y-%m-%d}','until':'{end_date:%Y-%m-%d}'}}",
            "access_token": self.meta_token,
        }
        if platform_filter := self._publisher_platform_filtering():
            params["filtering"] = platform_filter

        response = requests.get(url, params=params).json()
        if res := response["data"]:
            return self.apply_exchange_rate(res[0])

    # Ad-level insight fields requested in a single call. The Ads Manager
    # "performance & clicks" and "conversion & spend" presets are just column
    # groupings of this one dataset, so we pull everything at once.
    AD_INSIGHT_FIELDS = [
        "ad_id",
        "ad_name",
        "adset_name",
        "campaign_name",
        "account_currency",
        "impressions",
        "reach",
        "frequency",
        "spend",
        "clicks",
        "inline_link_clicks",
        "cpc",
        "cpm",
        "ctr",
        "quality_ranking",
        "engagement_rate_ranking",
        "conversion_rate_ranking",
        "actions",
        "action_values",
        "purchase_roas",
    ]

    # Flattened conversion columns -> the action_types to look up, in priority
    # order (omni_* spans web + app + in-store; the plain event is the fallback).
    AD_INSIGHT_ACTION_COLUMNS = {
        "landing_page_views": ["omni_landing_page_view", "landing_page_view"],
        "add_to_cart": ["omni_add_to_cart", "add_to_cart"],
        "initiate_checkout": ["omni_initiated_checkout", "initiate_checkout"],
        "purchases": ["omni_purchase", "purchase"],
    }
    AD_INSIGHT_ACTION_VALUE_COLUMNS = {
        "add_to_cart_value": ["omni_add_to_cart", "add_to_cart"],
        "purchase_value": ["omni_purchase", "purchase"],
    }

    @staticmethod
    def _first_action_value(items, action_types):
        """Return the first matching action_type value from an actions/values list."""
        by_type = {i.get("action_type"): i.get("value") for i in (items or [])}
        for action_type in action_types:
            if action_type in by_type:
                return by_type[action_type]
        return None

    def _flatten_ad_insight(self, row):
        """Flatten one raw insights row (with nested actions) into a flat dict.

        ALL monetary fields - spend and the conversion values (purchase_value,
        add_to_cart_value) - are normalised to JPY with the same per-row rate, so
        ROAS and value reconcile for non-JPY (e.g. KRW) accounts. Count metrics and
        Meta's own purchase_roas are currency-neutral and left as-is.
        """
        rate = self.jpy_rate(row.get("account_currency"), row.get("date_stop"))

        def to_jpy(value):
            return round(float(value) * rate) if value not in (None, "") else value

        out = {
            "report_start": row.get("date_start"),
            "report_end": row.get("date_stop"),
            "campaign_name": row.get("campaign_name"),
            "adset_name": row.get("adset_name"),
            "ad_name": row.get("ad_name"),
            "ad_id": row.get("ad_id"),
            "account_currency": row.get("account_currency"),
            "impressions": row.get("impressions"),
            "reach": row.get("reach"),
            "frequency": row.get("frequency"),
            "spend": to_jpy(row.get("spend")),
            "clicks_all": row.get("clicks"),
            "link_clicks": row.get("inline_link_clicks"),
            "ctr": row.get("ctr"),
            "cpc": row.get("cpc"),
            "cpm": row.get("cpm"),
            "quality_ranking": row.get("quality_ranking"),
            "engagement_rate_ranking": row.get("engagement_rate_ranking"),
            "conversion_rate_ranking": row.get("conversion_rate_ranking"),
        }
        actions = row.get("actions")
        action_values = row.get("action_values")
        for col, types in self.AD_INSIGHT_ACTION_COLUMNS.items():
            out[col] = self._first_action_value(actions, types)
        for col, types in self.AD_INSIGHT_ACTION_VALUE_COLUMNS.items():
            out[col] = to_jpy(self._first_action_value(action_values, types))
        out["purchase_roas_meta"] = self._first_action_value(
            row.get("purchase_roas"), ["omni_purchase", "purchase"]
        )
        spend = float(out.get("spend") or 0)
        purchase_value = out.get("purchase_value")
        out["roas_computed"] = (
            round(float(purchase_value) / spend, 4)
            if purchase_value and spend
            else None
        )
        return out

    # Meta's transient/throttle errors worth retrying. Code 1 / subcode 99 is the
    # generic "An unknown error occurred" that the Insights API throws on timeouts.
    META_TRANSIENT_ERROR_CODES = {1, 2, 4, 17, 341}

    def _meta_get_with_retry(self, url, params, max_retries=6):
        for attempt in range(max_retries):
            res = requests.get(url, params=params).json()
            error = res.get("error")
            if not error:
                return res
            transient = (
                error.get("code") in self.META_TRANSIENT_ERROR_CODES
                or error.get("error_subcode") == 99
            )
            if not transient or attempt == max_retries - 1:
                raise RuntimeError(f"Meta insights error: {error}")
            wait = 5 * (attempt + 1)
            logger.info(
                f"{self.__class__.__name__} Meta transient error "
                f"(code {error.get('code')}), retrying in {wait}s "
                f"({attempt + 1}/{max_retries})"
            )
            time.sleep(wait)

    def ad_insights(self, start_date, end_date, time_increment="monthly"):
        """All ad-level insights between two dates, one flat row per ad per period.

        ``time_increment`` is ``"monthly"`` (year-over-year) or ``1`` (daily). No
        spend filter is applied: zero-spend rows are harmless to weighted ROAS and
        carry delayed-attribution conversions worth keeping.

        Restricted to PUBLISHER_PLATFORMS (Instagram by default) via the insights
        ``filtering`` param, so Facebook placements are excluded at the source.

        Runs as an asynchronous insights job: the daily breakdown over a month is
        too large for the synchronous endpoint (it returns a generic code 1/99
        error), and the async job handles both small and large pulls reliably.
        """
        base = f"https://graph.facebook.com/{self.VERSION}/act_{self.meta_ad_account_id}/insights"
        params = {
            "level": "ad",
            "fields": ",".join(self.AD_INSIGHT_FIELDS),
            "time_range": f"{{'since':'{start_date:%Y-%m-%d}','until':'{end_date:%Y-%m-%d}'}}",
            "time_increment": time_increment,
            "access_token": self.meta_token,
        }
        if platform_filter := self._publisher_platform_filtering():
            params["filtering"] = platform_filter
        run = requests.post(base, params=params).json()
        if error := run.get("error"):
            raise RuntimeError(f"Meta insights job failed to start: {error}")
        run_id = run["report_run_id"]
        self._poll_meta_async_job(run_id)

        url = f"https://graph.facebook.com/{self.VERSION}/{run_id}/insights"
        result_params = {"limit": 500, "access_token": self.meta_token}
        raw = []
        page = 0
        while url:
            res = self._meta_get_with_retry(url, result_params)
            raw.extend(res["data"])
            page += 1
            logger.info(
                f"{self.__class__.__name__} ad_insights page {page}: "
                f"{len(res['data'])} rows ({len(raw)} total)"
            )
            url = res.get("paging", {}).get("next")
            result_params = None  # the 'next' url already carries the query string
        return [self._flatten_ad_insight(row) for row in raw]

    def meta_placement_breakdown(self, start_date, end_date, time_increment="monthly"):
        """Account spend / conversions split by publisher_platform (IG/FB/Threads/...).

        Surfaces where the budget actually goes, so Facebook spillover at near-zero
        ROAS is visible rather than hidden. Monetary fields normalised to JPY.
        """
        url = f"https://graph.facebook.com/{self.VERSION}/act_{self.meta_ad_account_id}/insights"
        params = {
            "level": "account",
            "fields": "account_currency,spend,actions,action_values,purchase_roas",
            "breakdowns": "publisher_platform",
            "time_increment": time_increment,
            "time_range": f"{{'since':'{start_date:%Y-%m-%d}','until':'{end_date:%Y-%m-%d}'}}",
            "limit": 500,
            "access_token": self.meta_token,
        }
        raw = []
        while url:
            res = self._meta_get_with_retry(url, params)
            raw.extend(res["data"])
            url = res.get("paging", {}).get("next")
            params = None
        rows = []
        for r in raw:
            rate = self.jpy_rate(r.get("account_currency"), r.get("date_stop"))
            spend = round(float(r.get("spend") or 0) * rate)
            value = self._first_action_value(
                r.get("action_values"), ["omni_purchase", "purchase"]
            )
            value = round(float(value) * rate) if value not in (None, "") else None
            rows.append(
                {
                    "month": r.get("date_start"),
                    "publisher_platform": r.get("publisher_platform"),
                    "spend": spend,
                    "purchases": self._first_action_value(
                        r.get("actions"), ["omni_purchase", "purchase"]
                    ),
                    "purchase_value": value,
                    "roas_computed": (
                        round(value / spend, 4) if value and spend else None
                    ),
                }
            )
        logger.info(
            f"{self.__class__.__name__} placement breakdown: {len(rows)} rows "
            f"({start_date} .. {end_date})"
        )
        return rows

    def _poll_meta_async_job(self, run_id, poll_seconds=5, max_polls=120):
        """Block until an async insights job completes; raise on failure/timeout."""
        status_url = f"https://graph.facebook.com/{self.VERSION}/{run_id}"
        for _ in range(max_polls):
            status = self._meta_get_with_retry(
                status_url, {"access_token": self.meta_token}
            )
            state = status.get("async_status")
            pct = status.get("async_percent_completion")
            if state == "Job Completed" and pct == 100:
                return
            if state in ("Job Failed", "Job Skipped"):
                raise RuntimeError(f"Meta async job {run_id} {state}")
            logger.info(
                f"{self.__class__.__name__} async job {run_id}: {state} ({pct}%)"
            )
            time.sleep(poll_seconds)
        raise RuntimeError(f"Meta async job {run_id} timed out")

    def dashboard_stats_meta(self, report_date, timeseries_by="month"):
        assert timeseries_by in ["week", "month"]
        date_from = (
            report_date - datetime.timedelta(days=6)
            if timeseries_by == "week"
            else (datetime.date(report_date.year, report_date.month, 1))
        )

        end_date = datetime.datetime.combine(
            report_date,
            datetime.time(23, 59, 59),
            tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo"),
        )
        start_date = datetime.datetime.combine(
            date_from,
            datetime.time(0, 0, 0),
            tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo"),
        )

        omni = self.omni_stats(start_date, end_date)
        paid = self.paid_stats(
            start_date,
            end_date,
        )
        row = [
            dict(
                report_date=f"{report_date:%Y-%m-%d}",
                reach_omni=omni["reach"],
                reach_paid=paid["reach"] if paid else "",
                profile_views_omni=omni["profile_views"],
                profile_views_paid=paid["inline_link_clicks"] if paid else "",
                saves=omni["saves"],
                spend=paid["spend"] if paid else "",
            )
        ]
        return pd.DataFrame(row)


def report_dates_for_weekly(report_year, report_month):
    import calendar

    month_matrix = calendar.monthcalendar(report_year, report_month)
    return [
        datetime.date(report_year, report_month, week[6])
        for week in month_matrix
        if week[6] != 0
    ]


def report_dates_for_monthly(report_year, report_month):
    import calendar

    _, last_day = calendar.monthrange(report_year, report_month)
    return [datetime.date(report_year, report_month, last_day)]


def run(
    brand: str, sheet_name: str, report_date: datetime.date, start_date: datetime.date
):
    import utils

    client = utils.client(brand)
    sheet_id = "14jUOdsb83EnEmQpXmmLmo3MtCK-CHiZ7bSocOLSjsFo"
    sheet_index = client.get_sheet_index_by_title(sheet_id, sheet_name)
    worksheet = client.gspread_client.open_by_key(sheet_id).get_worksheet(sheet_index)
    end_date = datetime.datetime.combine(
        report_date,
        datetime.time(23, 59, 59),
        tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo"),
    )
    start_date = datetime.datetime.combine(
        start_date,
        datetime.time(23, 59, 59),
        tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo"),
    )

    omni = client.omni_stats(start_date, end_date)
    paid = client.paid_stats(
        start_date=start_date + datetime.timedelta(seconds=1),
        end_date=end_date,
    )
    worksheet.insert_row(
        values=[
            f"{report_date:%Y/%m/%d}",
            brand,
            omni["reach"],
            paid["reach"] if paid else "",
            omni["profile_views"],
            paid["inline_link_clicks"] if paid else "",
            omni["saves"],
            "",
            "",
            "",
            "",
            paid["spend"] if paid else "",
        ],
        index=3,
    )


def run_range(brands, monthly_or_weekly, report_year, report_month):
    assert monthly_or_weekly.lower() in ["monthly", "weekly"]
    if monthly_or_weekly.lower() == "weekly":
        report_dates = report_dates_for_weekly(report_year, report_month)
        start_dates = [
            report_date - datetime.timedelta(days=7) for report_date in report_dates
        ]
    else:
        report_dates = report_dates_for_monthly(report_year, report_month)
        start_dates = [datetime.date(report_year, report_month, 1)]

    sheet_title = "Weekly" if monthly_or_weekly.lower() == "weekly" else "Monthly"

    for b in brands:
        print(b)
        for report_date, start_date in zip(report_dates, start_dates):
            run(b, sheet_title, report_date, start_date)


if __name__ == "__main__":
    brands = ["Apricot Studios", "BLOSSOM", "LEMEME", "Archivépke", "SSIL"]
    brands = ["ROH SEOUL"]
    run_range(brands, monthly_or_weekly="Weekly", report_year=2026, report_month=4)
    run("ROH SEOUL", "Weekly", datetime.date(2026, 5, 3), datetime.date(2026, 4, 27))
