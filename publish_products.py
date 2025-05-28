import datetime
import logging
import pytz
import utils

logging.basicConfig(level=logging.INFO)


def main():
    scheduled_time = pytz.timezone("Asia/Tokyo").localize(
        datetime.datetime(2025, 5, 30, 0, 0, 0)
    )
    client = utils.client("apricot-studios")
    products = client.products_by_tag("25_summer_2nd", additional_fields=["status"])
    # for product in products:
    #     assert (
    #         product["status"] == "DRAFT"
    #     ), f"Product {product['id']} is not in DRAFT status"

    publications = client.publications()
    for product in products:
        params = {"product_id": product["id"]}
        for publication in publications:
            params["publication_id"] = publication["id"]
            if publication["name"] == "Online Store":
                client.publish_by_product_id_and_publication_id(
                    scheduled_time=scheduled_time, **params
                )
            #     client.update_product_status(product["id"], "ACTIVE")
            # else:
            #     client.publish_by_product_id_and_publication_id(**params)


if __name__ == "__main__":
    main()
