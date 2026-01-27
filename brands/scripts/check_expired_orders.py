import datetime
import logging
import os
import zoneinfo

logging.basicConfig(level=logging.INFO)

import utils


def check(brand, email_recipients):
    asof = (datetime.datetime.today() - datetime.timedelta(days=14)).astimezone(
        zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client = utils.client(brand.lower())
    orders = client.orders_expired(asof=asof)

    body = ""
    if orders:
        body += "orders expired\n"
        for o in sorted(
            orders, key=lambda o: datetime.datetime.fromisoformat(o["processedAt"])
        ):
            body += f"{datetime.datetime.fromisoformat(o["processedAt"]).astimezone(zoneinfo.ZoneInfo("Asia/Tokyo")).date()}\t{o["name"]}\n"
        body += "\n"

    if body:
        print(body)
        client.send_email(
            f"{brand} - expired orders ",
            body,
            email_recipients,
        )


def main():
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
        check(brand, os.environ["EXPIRED_ORDERS_NOTIFYEES"].split(","))


if __name__ == "__main__":
    main()
