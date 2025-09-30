import logging
import pprint
import utils
from product_create import product_info_list_from_sheet_color_and_size

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("apricot-studios")
    products = client.products_by_tag("Daughter")
    for product in products:
        tags = ",".join(product["tags"] + ["APRICOT", "DAUGHTER"])
        print(product["title"], tags)
        pprint.pprint(client.update_product_tags(product["id"], tags))


if __name__ == "__main__":
    main()
