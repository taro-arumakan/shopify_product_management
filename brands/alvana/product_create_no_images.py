import logging

logging.basicConfig(level=logging.INFO)

from brands.alvana.client import AlvanaClient


def main():
    sheet_name = "26SS Product Master"
    client = AlvanaClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag="26ss",
    )
    product_inputs = client.product_inputs_by_sheet_name(sheet_name)
    for product_input in product_inputs:
        product_input["options"] = [
            o for o in product_input["options"] if o["drive_link"] == "no image"
        ]
        if product_input["options"]:
            product_input["title"] += " (no image)"
            res = client.process_product_input(product_input)
            client.update_product_status(res["create_product"]["id"], "UNLISTED")


if __name__ == "__main__":
    main()
