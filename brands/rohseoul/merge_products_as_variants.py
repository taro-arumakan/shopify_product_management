import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("rohseoul")
    titles = [
        "Curly tote bag",
        "Goody bag",
        "Large aline shoulder bag",
        "Large mug shoulder bag nylon",
        "Medium around hobo bag",
        "Medium knot shoulder bag",
        "Medium mug shoulder bag nylon",
        "Medium pebble shoulder bag",
        "Medium tin square tote bag",
        "Mini around hobo bag",
        "Mini mug tote bag",
        "Mini pulpy hobo bag",
    ]
    for title in titles:
        client.merge_products_as_variants(title, "Shop location")


if __name__ == "__main__":
    main()
