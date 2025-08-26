import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("rohseoul")
    titles = [
        "Rowie shoulder bag Nylon",
        "Mini Pulpy hobo bag Nylon",
    ]
    for title in titles:
        client.merge_products_as_variants(title, "Shop location")


if __name__ == "__main__":
    main()
