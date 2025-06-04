import logging
import utils
from brands.apricotstudios.product_create import (
    product_info_list_from_sheet_color_and_size,
    text_to_html_tables_and_paragraphs,
)
from product_metafields_update_size_table_html import update_size_table_html_metafield
from product_description_include_metafield_value import (
    update_description_include_metafield_value,
)

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("apricot-studios")
    product_info_list = product_info_list_from_sheet_color_and_size(
        client, client.sheet_id, "Products Master"
    )
    for product_info in product_info_list:
        if product_info["title"] in [
            "SUMMER MOTIVE SOCKS 3pcs",
        ]:
            size_text = product_info.get("size_text")
            if size_text:
                size_table_html = text_to_html_tables_and_paragraphs(size_text)
                update_size_table_html_metafield(
                    client, product_info["title"], size_table_html
                )
                update_description_include_metafield_value(
                    client, product_info["title"]
                )
            else:
                logging.warning(
                    f"No size information found for {product_info['title']}"
                )


if __name__ == "__main__":
    main()
