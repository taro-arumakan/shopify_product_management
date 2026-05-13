import logging
from brands.alvana.client import AlvanaClient

logging.basicConfig(level=logging.INFO)


def main():

    client = AlvanaClient(
        product_sheet_start_row=1,
    )
    product_inputs = client.product_inputs_by_sheet_name("26SS Product Master")
    for pi in product_inputs:
        remove_skus = []
        for color_option in pi["options"]:
            if color_option["drive_link"] == "no image":
                remove_skus += [v["sku"] for v in color_option["options"]]
        if remove_skus:
            product = client.product_by_title(pi["title"])
            variant_ids = [client.variant_id_by_sku(sku) for sku in remove_skus]
            print(
                f"going to remove {len(variant_ids)} variants from {product['title']} - {product['id']}: {variant_ids}"
            )
            client.remove_product_variants(product["id"], variant_ids)


if __name__ == "__main__":
    main()
