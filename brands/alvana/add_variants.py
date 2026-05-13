import logging

logging.basicConfig(level=logging.INFO)

from brands.alvana.client import AlvanaClient


def main():
    sheet_name = "26SS Product Master 変更"
    client = AlvanaClient(product_sheet_start_row=1)
    product_inputs = client.product_inputs_by_sheet_name(sheet_name)
    for i, pi in enumerate(product_inputs):
        if pi["title"] == "空紡 TANK TOP TEE SHIRTS":
            break
    product_inputs = product_inputs[i:]

    res = client.check_existing_skus(product_inputs)
    res += client.check_images_link(product_inputs)
    if res:
        for r in res:
            print(r)
        raise RuntimeError("failed sanity check")
    for product_input in product_inputs:
        new_color_options = [
            o
            for o in product_input["options"]
            if o["remarks"] == "NEW COLOR" and o["drive_link"] != "no image"
        ]
        new_size_options = [
            o for o in product_input["options"] if o["remarks"] == "NEW SIZE"
        ]
        if new_color_options:
            product_input["options"] = new_color_options
            client.add_variants_from_product_input(product_input)
        if new_size_options:
            # TODO size only addition not supported
            pass


if __name__ == "__main__":
    main()
