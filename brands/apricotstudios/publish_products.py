import datetime
import logging
import pytz
import utils

logging.basicConfig(level=logging.INFO)

handles = [
    "mare-cardigan",
    "varsity-setup",
    "if-knit-top",
    "pigment-wave-setup",
    "mar-t-shirt",
    "grace-setup",
    "leats-setup",
    "leats-setup",
    "pigment-wave-setup",
    "easy-pants",
    "easy-pants",
    "25-summer-sandy-suit",
    "25-jelly-stripe-indoorwear",
    "color-denim-pants",
    "fave-pants",
    "fave-pants",
    "fave-pants",
    "fave-pants",
    "fave-pants",
    "summer-marin-eyelet-socks-2pcs",
    "summer-marin-eyelet-socks-2pcs",
    "summer-motive-socks-3pcs",
    "bejou-leggings",
    "bejou-leggings",
    "bejou-leggings",
    "bejou-leggings",
    "babycot-bubble-bodysuit",
    "babycot-bubble-bodysuit",
    "babycot-breeze-romper",
    "babycot-breeze-romper",
    "babycot-blooming-romper",
    "babycot-blooming-romper",
    "babycot-ivy-collar-suit",
    "babycot-peony-ruffle-setup",
    "babycot-sunnypop-bloomer",
    "babycot-sunnypop-bloomer",
    "babycot-lemon-seersucker-setup",
    "babycot-lemon-seersucker-setup",
    "babycot-rabbit-dot-bonnet",
    "babycot-ivy-frill-bonnet",
]

# XXX move to client.activate_and_publish_by_product_id


def main():
    scheduled_time = pytz.timezone("Asia/Tokyo").localize(
        datetime.datetime(2025, 8, 18, 10, 0, 0)
    )
    client = utils.client("apricot-studios")
    publications = client.publications()
    for handle in set(handles):
        product = client.product_by_handle(handle)
        logging.info(
            f"Publishing product {product['id']} - {product['title']} at {scheduled_time}"
        )
        params = {"product_id": product["id"]}
        for publication in publications:
            params["publication_id"] = publication["id"]
            if publication["name"] == "Online Store":
                client.publish_by_product_id_and_publication_id(
                    scheduled_time=scheduled_time, **params
                )
                client.update_product_status(product["id"], "ACTIVE")


if __name__ == "__main__":
    main()
