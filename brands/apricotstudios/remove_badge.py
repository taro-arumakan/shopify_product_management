import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("apricot-studios")
    products = client.products_by_tag("campaign_eligible")

    for product in products:
        tags = [t for t in product["tags"] if t != "campaign_eligible"]
        client.update_product_tags(product["id"], tags)
        client.update_badges_metafield(product["id"], [])


if __name__ == "__main__":
    main()
