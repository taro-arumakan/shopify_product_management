import datetime
import zoneinfo
import logging
import utils


logging.basicConfig(level=logging.INFO)


def main():
    scheduled_time = datetime.datetime(
        2025, 10, 24, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    client = utils.client("rohseoul")
    products = client.products_by_tag("2025-10-24")
    for product in products:
        client.activate_and_publish_by_product_id(
            product["id"], scheduled_time=scheduled_time
        )


if __name__ == "__main__":
    main()
