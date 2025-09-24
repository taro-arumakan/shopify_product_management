import datetime
import logging
import pytz
import utils

logging.basicConfig(level=logging.INFO)


def main():
    scheduled_time = pytz.timezone("Asia/Tokyo").localize(
        datetime.datetime(2025, 9, 26, 0, 0, 0)
    )
    client = utils.client("gbhjapan")
    products = client.products_by_tag("2025-09-26")
    for product in products:
        client.activate_and_publish_by_product_id(
            product["id"], scheduled_time=scheduled_time
        )


if __name__ == "__main__":
    main()
