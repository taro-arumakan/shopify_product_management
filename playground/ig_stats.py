import datetime
import os
import requests
import pandas as pd
import zoneinfo

from dotenv import load_dotenv

load_dotenv(override=True)

VERSION = "v25.0"


def _get_omni_stat_value_by_key(d, k):
    return [dd for dd in d if dd["name"] == k][0]["total_value"]["value"]


def omni_stats(ig_user_id, token, start_date, end_date):
    print(f"omni stats between {start_date} and {end_date}")
    acc_url = f"https://graph.facebook.com/{VERSION}/{ig_user_id}/insights"
    acc_res = requests.get(
        acc_url,
        params={
            "metric": "views,reach,profile_views,website_clicks,saves,total_interactions",
            "metric_type": "total_value",
            "period": "day",
            "since": int(start_date.timestamp()),
            "until": int(end_date.timestamp()),
            "access_token": token,
        },
    )

    acc_data = acc_res.json()["data"]
    return {
        k: _get_omni_stat_value_by_key(acc_data, k)
        for k in [
            "views",
            "reach",
            "saves",
            "profile_views",
            "website_clicks",
            "total_interactions",
        ]
    }


def paid_stats(
    ad_account_id, token, start_date: datetime.datetime, end_date: datetime.datetime
):
    print(f"paid stats between {start_date} and {end_date}")
    url = f"https://graph.facebook.com/{VERSION}/act_{ad_account_id}/insights"

    # Note: Marketing API uses 'YYYY-MM-DD' strings for time_range,
    # unlike the IG API which uses Unix timestamps.

    params = {
        "level": "account",
        "fields": "impressions,reach,inline_link_clicks,outbound_clicks,spend",
        # "filtering": "[{'field':'publisher_platform','operator':'IN','value':['instagram']}]",
        "time_range": f"{{'since':'{start_date:%Y-%m-%d}','until':'{end_date:%Y-%m-%d}'}}",
        "access_token": token,
    }

    response = requests.get(url, params=params).json()
    return response["data"][0]


if __name__ == "__main__":
    brands = ["blossomhcompany", "lememek", "archive-epke", "ssilkr", "apricot-studios"]
    report_date = datetime.date(2026, 4, 14)
    end_date = datetime.datetime.combine(
        report_date, datetime.time(23, 59, 59), tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    start_date = end_date - datetime.timedelta(days=7)
    for b in brands:
        meta_token = os.environ[f"{b}-META_TOKEN"]
        ig_user_id = os.environ[f"{b}-IG_USER_ID"]
        ad_account_id = os.environ[f"{b}-META_AD_ACCOUNT_ID"]

        omni = omni_stats(ig_user_id, meta_token, start_date, end_date)
        paid = paid_stats(
            ad_account_id,
            meta_token,
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
        print(f"Omni Link Clicks: {omni['website_clicks']}")
        print(f"Paid Link Clicks: {paid['inline_link_clicks']}")
        print(f"Omni Saves: {omni['saves']}")
        print(f"Spend: {paid['spend']}")
        print()
