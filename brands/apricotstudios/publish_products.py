import datetime
import logging
import pytz
import utils

logging.basicConfig(level=logging.INFO)


def main():
    scheduled_time = pytz.timezone("Asia/Tokyo").localize(
        datetime.datetime(2025, 9, 25, 0, 0, 0)
    )
    client = utils.client("apricot-studios")
    products = client.products_by_collection_id("457808675072")
    for product in products:
        client.activate_and_publish_by_product_id(
            product["id"], scheduled_time=scheduled_time
        )


if __name__ == "__main__":
    main()
