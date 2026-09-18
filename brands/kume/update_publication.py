import datetime
import logging
import zoneinfo
import utils

logging.basicConfig(level=logging.DEBUG)


def main():
    client = utils.client("kume")
    scheduled_time = datetime.datetime(
        2026, 9, 23, 11, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    products = client.products_by_tag("26_0923_FW_3")
    for p in products:
        client.publish_by_product_or_collection_id(
            p["id"], scheduled_time=scheduled_time
        )


if __name__ == "__main__":
    main()
