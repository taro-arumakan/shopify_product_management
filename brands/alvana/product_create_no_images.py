import logging

logging.basicConfig(level=logging.INFO)

from brands.alvana.client import AlvanaClient


def main():
    sheet_name = "26SS Product Master 変更"
    client = AlvanaClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag="26ss",
    )
    product_inputs = client.product_inputs_by_sheet_name(sheet_name)
    for i, pi in enumerate(product_inputs):
        if pi["title"] == "空紡 S/S TEE SHIRTS":
            break
    product_inputs = product_inputs[i:]
    for product_input in product_inputs:
        product_input["options"] = [
            o
            for o in product_input["options"]
            if o["drive_link"] == "no image" and o["remarks"] == "NEW COLOR"
        ]
        if product_input["options"]:
            product_input["title"] += " (no image)"
            res = client.create_product_by_product_input(
                product_input,
                client.VENDOR,
                description_html="",
                tags=["26ss"],
            )
            client.update_product_status(res["id"], "UNLISTED")
            client.enable_and_activate_inventory_by_product_input(
                product_input, client.LOCATIONS
            )
            client.update_stock(product_input)


if __name__ == "__main__":
    main()
