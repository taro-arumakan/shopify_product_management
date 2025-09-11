import datetime
import logging
import pytz
import utils

logging.basicConfig(level=logging.INFO)


def main():
    scheduled_time = pytz.timezone("Asia/Tokyo").localize(
        datetime.datetime(2025, 9, 24, 0, 0, 0)
    )
    client = utils.client("archive-epke")
    products = client.products_by_tag("2025-09-26")
    tags_map = {"2025-09-26": "2025-09-24"}
    for product in products:
        client.activate_and_publish_by_product_id(
            product["id"], scheduled_time=scheduled_time
        )

        tags = [tags_map.get(t, t) for t in product["tags"]]
        client.update_product_tags(product["id"], ",".join(tags))


if __name__ == "__main__":
    main()
