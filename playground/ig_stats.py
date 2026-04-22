import datetime
import os
import requests
import pandas as pd
import zoneinfo

from dotenv import load_dotenv

load_dotenv(override=True)

META_TOKEN = os.environ["blossomhcompany-META_TOKEN"]
IG_USER_ID = os.environ["blossomhcompany-IG_USER_ID"]
AD_ACCOUNT_ID = os.environ["blossomhcompany-META_AD_ACCOUNT_ID"]

META_TOKEN = os.environ["lememek-META_TOKEN"]
IG_USER_ID = os.environ["lememek-IG_USER_ID"]
AD_ACCOUNT_ID = os.environ["lememek-META_AD_ACCOUNT_ID"]

META_TOKEN = os.environ["archive-epke-META_TOKEN"]
IG_USER_ID = os.environ["archive-epke-IG_USER_ID"]
AD_ACCOUNT_ID = os.environ["archive-epke-META_AD_ACCOUNT_ID"]

META_TOKEN = os.environ["ssilkr-META_TOKEN"]
IG_USER_ID = os.environ["ssilkr-IG_USER_ID"]
AD_ACCOUNT_ID = os.environ["ssilkr-META_AD_ACCOUNT_ID"]


VERSION = "v25.0"


def omni_stats():
    today = datetime.datetime(
        2026, 4, 14, 23, 59, 59, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    seven_days_ago = today - datetime.timedelta(days=7)
    today = int(today.timestamp())
    seven_days_ago = int(seven_days_ago.timestamp())

    # url = f"https://graph.facebook.com/{VERSION}/{IG_USER_ID}/media"
    # res = requests.get(
    #     url,
    #     params={"since": seven_days_ago, "until": today, "META_TOKEN": META_TOKEN},
    # )

    # total_reach = 0
    # total_saves = 0

    # for item in res.json()["data"]:
    #     i_url = f"https://graph.facebook.com/{VERSION}/{item['id']}/insights"
    #     i_res = requests.get(
    #         i_url, params={"metric": "reach,saved", "META_TOKEN": META_TOKEN}
    #     )

    #     # Extract values
    #     metrics = {m["name"]: m["values"][0]["value"] for m in i_res.json()["data"]}
    #     total_reach += metrics.get("reach", 0)
    #     total_saves += metrics.get("saved", 0)

    # 3. Fetch Account-Level Profile Visits
    acc_url = f"https://graph.facebook.com/{VERSION}/{IG_USER_ID}/insights"
    acc_res = requests.get(
        acc_url,
        params={
            "metric": "profile_views,website_clicks,reach,saves,total_interactions",
            "metric_type": "total_value",
            "period": "day",
            "since": seven_days_ago,
            "until": today,
            "access_token": META_TOKEN,
        },
    )

    acc_data = acc_res.json()["data"]

    reach = [d for d in acc_data if d["name"] == "reach"][0]["total_value"]["value"]
    saves = [d for d in acc_data if d["name"] == "saves"][0]["total_value"]["value"]
    profile_views = [d for d in acc_data if d["name"] == "profile_views"][0][
        "total_value"
    ]["value"]
    website_clicks = [d for d in acc_data if d["name"] == "website_clicks"][0][
        "total_value"
    ]["value"]
    total_interactions = [d for d in acc_data if d["name"] == "total_interactions"][0][
        "total_value"
    ]["value"]

    print("reach:", reach)
    print("saves:", saves)
    print("profile_views:", profile_views)
    print("website_clicks:", website_clicks)
    print("total_interactions:", total_interactions)


def get_paid_only_metrics(ad_account_id, token, since, until):
    url = f"https://graph.facebook.com/{VERSION}/act_{ad_account_id}/insights"

    params = {
        "level": "account",
        "fields": "reach,impressions,inline_link_clicks,spend",
        "time_range": f"{{'since':'{since}','until':'{until}'}}",
        "access_token": token,
    }

    response = requests.get(url, params=params).json()
    return response["data"][0]


def get_media_performance():
    # 1. Fetch recent media
    media_url = f"https://graph.facebook.com/{VERSION}/{IG_USER_ID}/media"
    res = requests.get(media_url, params={"access_token": META_TOKEN})
    media_ids = [item["id"] for item in res.json()["data"]]

    report_data = []

    # 2. Loop through and get metrics
    for m_id in media_ids:
        metrics = "reach,saved,total_interactions"
        insight_url = f"https://graph.facebook.com/{VERSION}/{m_id}/insights"
        i_res = requests.get(
            insight_url, params={"metric": metrics, "access_token": META_TOKEN}
        )

        # Flatten the nested JSON for your DataFrame
        stats = {
            m["name"]: m["values"][0]["value"] for m in i_res.json().get("data", [])
        }
        stats["media_id"] = m_id
        report_data.append(stats)

    return pd.DataFrame(report_data)


# # Run and export
# df = get_media_performance()
# df.to_csv('weekly_ig_content_report.csv')


def list_brand_ids(token):
    url = f"https://graph.facebook.com/{VERSION}/me/accounts"
    params = {"fields": "name,instagram_business_account", "access_token": token}

    response = requests.get(url, params=params).json()

    for page in response.get("data", []):
        ig_account = page.get("instagram_business_account")
        if ig_account:
            print(f"Brand Name: {page['name']}")
            print(f"IG User ID: {ig_account['id']}")
            print("-" * 30)
        else:
            print(f"Brand Name: {page['name']} (No IG account linked)")


if __name__ == "__main__":
    omni_stats()
    # Note: Marketing API uses 'YYYY-MM-DD' strings for time_range,
    # unlike the IG API which uses Unix timestamps.
    paid_stats = get_paid_only_metrics(
        AD_ACCOUNT_ID, META_TOKEN, "2026-04-08", "2026-04-14"
    )

    print(f"Paid Impressions: {paid_stats['impressions']}")
    print(f"Paid Reach: {paid_stats['reach']}")
    print(f"Paid Link Clicks: {paid_stats['inline_link_clicks']}")
    print(f"Spend: {paid_stats['spend']}")
