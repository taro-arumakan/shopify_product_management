import datetime
import logging
import os
import zoneinfo
import dotenv
import utils

logging.basicConfig(level=logging.INFO)


def check(brand, email_recipients):
    asof = datetime.datetime.combine(datetime.date.today(), datetime.time())
    asof = asof - datetime.timedelta(days=14)
    asof = asof.astimezone(zoneinfo.ZoneInfo("Asia/Tokyo"))

    client = utils.client(brand.lower())
    orders = client.orders_expired(asof=asof)

    body = ""
    if orders:
        body += "orders in expired status and 14 days past\n"
        tz = zoneinfo.ZoneInfo("Asia/Tokyo")
        for order in orders:
            order["processedAt"] = datetime.datetime.fromisoformat(
                order["processedAt"]
            ).astimezone(tz)
        for o in sorted(orders, key=lambda o: o["processedAt"]):
            body += f"{o["processedAt"].date()}\t{o["name"]}\n"
        body += "\n"

    if body:
        print(body)
        client.send_email(
            f"{brand} - expired orders ",
            body,
            email_recipients,
        )


def main():
    assert dotenv.load_dotenv(override=True)
    brands = [
        "a-and-stores",
        "apricot-studios",
        "archive-epke",
        "blossom",
        "gbh",
        "kume",
        "lememe",
        "roh",
        "ssil",
    ]
    for brand in brands:
        logging.info(f"Checking {brand}...")
        check(brand, os.environ["NOTIFYEES_EXPIRED_ORDERS"].split(","))


if __name__ == "__main__":
    main()
