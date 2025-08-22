import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("rohseoul")
    titles = [
        "Large mug shoulder bag",
        "Medium mug shoulder bag",
        "Mini pulpy hobo bag suede",
        "Mini root backpack nylon",
        "Mini tin square tote bag",
        "Mini tin square tote bag suede",
        "Oval button wallet",
        "Pulpy crossbody bag",
        "Pulpy crossbody bag nylon",
        "Pulpy crossbody bag suede",
        "Pulpy hobo bag",
        "Pulpy hobo bag nylon",
        "Ripple shoulder bag",
        "Roh ball cap",
        "Rohbit wappen t-shirt",
        "Root backpack nylon",
        "Taco shoulder bag",
        "Tin square shoulder bag",
    ]
    for title in titles:
        client.merge_products_as_variants(title, "Shop location")


if __name__ == "__main__":
    main()
