import datetime
import zoneinfo
import logging
import utils


logging.basicConfig(level=logging.INFO)


def main():
    scheduled_time = datetime.datetime(
        2025, 9, 1, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    client = utils.client("kumej")
    products = client.products_by_tag("25FW")
    for product in products:
        logging.info(f"publishing product: {product['title']}")
        client.activate_and_publish_by_product_id(
            product["id"], scheduled_time=scheduled_time
        )


if __name__ == "__main__":
    main()
