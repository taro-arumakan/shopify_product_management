import datetime
import logging
import os
import zoneinfo
import dotenv
import utils

logging.basicConfig(level=logging.INFO)


def process(brand, email_recipients, dryrun=True):

    client = utils.client(brand.lower())
    orders = client.get_expired_orders_for_cancellation()

    body = ""
    if orders:
        body += "Going to cancel these orders in expired status and 14 days past:\n"
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
            f"{brand} - expired orders",
            body,
            email_recipients,
        )
    for order in orders:
        print(f"Closing {order['name']}")
        if not dryrun:
            client.order_cancel_and_close(
                order,
                notify_customer=True,
                staff_note="Auto-cancelled: Payment expired",
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
        process(brand, os.environ["NOTIFYEES_EXPIRED_ORDERS"].split(","))


if __name__ == "__main__":
    main()
