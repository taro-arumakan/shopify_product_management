import datetime
import logging
import requests
import zoneinfo


logger = logging.getLogger(__name__)


class MetaReportingInterface:
    def __init__(self, fb_page_id, ig_user_id, meta_ad_account_id, meta_token):
        self.VERSION = "v25.0"
        self.fb_page_id = fb_page_id
        self.ig_user_id = ig_user_id
        self.meta_ad_account_id = meta_ad_account_id
        self.meta_token = meta_token

    def _get_omni_ig_stat_value_by_key(self, d, k):
        return [dd for dd in d if dd["name"] == k][0]["total_value"]["value"]

    def omni_ig_stags(self, start_date, end_date):
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
            for k in [
                "views",
                "reach",
                "saves",
                "profile_views",
                "website_clicks",
                "total_interactions",
            ]
        }

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
            "page_post_engagements": "total_interactions",  # Total Clicks/Actions
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
        ig_data = self.omni_ig_stags(start_date=start_date, end_date=end_date)
        fb_data = self.omni_fb_stats(start_date=start_date, end_date=end_date)
        return {
            k: ig_data[k] + fb_data[k]
            for k in [
                "views",
                "reach",
                # "saves",
                "profile_views",
                # "website_clicks",
                "total_interactions",
            ]
        }

    def paid_stats(self, start_date: datetime.datetime, end_date: datetime.datetime):
        logger.info(f"paid stats between {start_date} and {end_date}")
        url = f"https://graph.facebook.com/{self.VERSION}/act_{self.meta_ad_account_id}/insights"

        # Note: Marketing API uses 'YYYY-MM-DD' strings for time_range,
        # unlike the IG API which uses Unix timestamps.

        params = {
            "level": "account",
            "fields": "impressions,reach,inline_link_clicks,outbound_clicks,spend",
            # "filtering": "[{'field':'publisher_platform','operator':'IN','value':['instagram']}]",
            "time_range": f"{{'since':'{start_date:%Y-%m-%d}','until':'{end_date:%Y-%m-%d}'}}",
            "access_token": self.meta_token,
        }

        response = requests.get(url, params=params).json()
        return response["data"][0]


if __name__ == "__main__":
    import utils

    brands = ["apricot-studios", "blossomhcompany", "lememek", "archive-epke", "ssilkr"]
    report_date = datetime.date(2026, 4, 14)
    end_date = datetime.datetime.combine(
        report_date, datetime.time(23, 59, 59), tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    start_date = end_date - datetime.timedelta(days=7)
    for b in brands:
        client = utils.client(b)
        omni = client.omni_stats(start_date, end_date)
        paid = client.paid_stats(
            start_date=start_date + datetime.timedelta(seconds=1),
            end_date=end_date,
        )
        print(b)
        print(f"Omni Impressions: {omni['views']}")
        print(f"Paid Impressions: {paid['impressions']}")
        print(f"Omni Reach: {omni['reach']}")
        print(f"Paid Reach: {paid['reach']}")
        print(f"Omni Profile Views: {omni['profile_views']}")
        print(
            f"Paid Profile Views (Approximate): {paid['outbound_clicks'][0]['value']}"
        )
        # TODO investigate interactions
        print(f"Omni Link Clicks: {omni['total_interactions']}")
        print(f"Paid Link Clicks: {paid['inline_link_clicks']}")
        # print(f"Omni Saves: {omni['saves']}")
        print(f"Spend: {paid['spend']}")
        print()
