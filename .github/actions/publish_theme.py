import logging
import sys

logging.basicConfig(level=logging.INFO)
import utils


def main():
    """
    shop_name               archive-epke
    theme_name              26SS collection 1st open 15% sale 3/5-3/15
    """

    shop_name = sys.argv[1]
    theme_name = sys.argv[2]

    client = utils.client(shop_name)
    theme_id = client.theme_id_by_theme_name(theme_name)
    logging.info(f"publishing on {client.VENDOR} - {theme_id}: {theme_name}")
    client.publish_theme(theme_id)


if __name__ == "__main__":
    main()
