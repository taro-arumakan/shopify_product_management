import logging
import pprint
import utils
from product_create import product_info_list_from_sheet_color_and_size

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("apricot-studios")
    product_info_list = product_info_list_from_sheet_color_and_size(
        client, client.sheet_id, "9.25 25Autumn(2nd)"
    )
    for product_info in product_info_list:
        product = client.product_by_title(product_info["title"])
        tags = ",".join(
            [
                product_info["collection"],
                product_info["category"],
                product_info["release_date"],
            ]
            + ["New Arrival", "25 Autumn", "25 Autumn 2nd"]
        )
        print(product_info["title"], tags)
        pprint.pprint(client.update_product_tags(product["id"], tags))


if __name__ == "__main__":
    main()
