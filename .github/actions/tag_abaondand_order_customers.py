import datetime
import logging

logging.basicConfig(level=logging.INFO)

import utils


def get_eligible_customers(client, rundate):
    threshold_date = rundate - datetime.timedelta(days=7)
    customers = client.customers_by_query(
        customers_query_string=f"last_abandoned_order_date:>={threshold_date:%Y-%m-%d}",
        orders_query_string="discount_code:auto_5%_off",
    )
    return [customer for customer in customers if not customer["orders"]["nodes"]]


def tag(brand):
    client = utils.client(brand)
    for customer in get_eligible_customers(client, datetime.date.today()):
        logging.info(
            f"tagging customer {customer['defaultEmailAddress']['emailAddress']}{customer['firstName']} {customer['lastName']}"
        )
        client.update_customers_tags(
            customer["id"], ",".join(customer["tags"] + ["auto_5%_off"])
        )


def untag(brand):
    client = utils.client(brand)
    for customer in client.customers_by_query(
        customers_query_string="tag:'auto_5%_off'"
    ):
        logging.info(
            f"untagging customer {customer['defaultEmailAddress']['emailAddress']}{customer['firstName']} {customer['lastName']}"
        )
        client.update_customers_tags(
            customer["id"],
            ",".join(tag for tag in customer["tags"] if tag != "auto_5%_off"),
        )


brands = [
    "Archivépke",
    "KUMÉ",
    "LEMEME",
]


def tag_brands():
    for brand in brands:
        tag(brand)


def untag_brands():
    for brand in brands:
        untag(brand)


if __name__ == "__main__":
    untag_brands()
