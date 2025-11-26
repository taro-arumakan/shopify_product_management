import logging
import pprint
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("apricot-studios")
    product_info_list = client.product_info_list_from_sheet("11.20 25Winter_clone")
    for pi in product_info_list:
        product = client.product_by_title(pi["title"])
        tags = product["tags"] + ["25 Winter"]
        pprint.pprint(client.update_product_tags(product["id"], tags))


if __name__ == "__main__":
    main()
