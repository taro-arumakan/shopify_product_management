import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("archive-epke")
    titles = [
        "Ridge shoulder bag",
    ]
    for title in titles:
        client.merge_products_as_variants(title)


if __name__ == "__main__":
    main()
