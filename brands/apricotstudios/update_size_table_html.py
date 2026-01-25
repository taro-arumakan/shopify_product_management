import logging
import utils
from brands.apricotstudios.client import ApricotStudiosClient

logging.basicConfig(level=logging.INFO)


def main():
    client = ApricotStudiosClient()
    client.sheet_id = "1QOs5sQC7GP_-A4sljYekbI4UWT2ibxQ01HBxcs3BUPc"
    product_inputs = client.product_inputs_by_sheet_name("9.25 25Autumn(2nd)")
    for product_input in product_inputs:
        title = product_input["title"]
        size_table_html = client.get_size_field(product_input)
        product_id = client.product_id_by_title(title)
        client.update_size_table_html_metafield(product_id, size_table_html)


if __name__ == "__main__":
    main()
