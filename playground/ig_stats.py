import datetime
import os
import requests
import pandas as pd

from dotenv import load_dotenv

load_dotenv(override=True)

ACCESS_TOKEN = os.environ["blossomhcompany-IG_TOKEN"]
IG_USER_ID = os.environ["blossomhcompany-IG_USER_ID"]
VERSION = "v25.0"


def stats():
    today = datetime.datetime.now()
    seven_days_ago = int((today - datetime.timedelta(days=7)).timestamp())

    url = f"https://graph.facebook.com/{VERSION}/{IG_USER_ID}/media"
    res = requests.get(
        url,
        params={"since": seven_days_ago, "until": today, "access_token": ACCESS_TOKEN},
    )

    total_reach = 0
    total_saves = 0

    for item in res.json()["data"]:
        i_url = f"https://graph.facebook.com/{VERSION}/{item['id']}/insights"
        i_res = requests.get(
            i_url, params={"metric": "reach,saved", "access_token": ACCESS_TOKEN}
        )

        # Extract values
        metrics = {m["name"]: m["values"][0]["value"] for m in i_res.json()["data"]}
        total_reach += metrics.get("reach", 0)
        total_saves += metrics.get("saved", 0)

    # 3. Fetch Account-Level Profile Visits
    acc_url = f"https://graph.facebook.com/{VERSION}/{IG_USER_ID}/insights"
    acc_res = requests.get(
        acc_url,
        params={
            "metric": "profile_views,website_clicks",
            "metric_type": "total_value",
            "period": "day",
            "since": seven_days_ago,
            "until": today,
            "access_token": ACCESS_TOKEN,
        },
    )

    # Sum up the daily profile views for the week
    profile_visits = [
        d for d in acc_res.json()["data"] if d["name"] == "profile_views"
    ][0]["total_value"]["value"]
    website_clicks = [
        d for d in acc_res.json()["data"] if d["name"] == "website_clicks"
    ][0]["total_value"]["value"]

    print("total reach:", total_reach)
    print("total_saves:", total_saves)
    print("profile_visits:", profile_visits)
    print("website_clicks:", website_clicks)


def get_media_performance():
    # 1. Fetch recent media
    media_url = f"https://graph.facebook.com/{VERSION}/{IG_USER_ID}/media"
    res = requests.get(media_url, params={"access_token": ACCESS_TOKEN})
    media_ids = [item["id"] for item in res.json()["data"]]

    report_data = []

    # 2. Loop through and get metrics
    for m_id in media_ids:
        metrics = "reach,saved,total_interactions"
        insight_url = f"https://graph.facebook.com/{VERSION}/{m_id}/insights"
        i_res = requests.get(
            insight_url, params={"metric": metrics, "access_token": ACCESS_TOKEN}
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
    stats()
