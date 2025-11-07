import json
import utils


def main():
    client = utils.client("ssil")
    products = client.products_by_tag("Ring")
    for product in products:
        size_text_metafield = [
            n for n in product["metafields"]["nodes"] if n["key"] == "size_text"
        ]
        size_text_metafield_value = json.loads(size_text_metafield[0]["value"])
        updated_value = client.append_ring_size_guide_link(size_text_metafield_value)
        client.update_product_metafield(
            product["id"], "custom", "size_text", json.dumps(updated_value)
        )


if __name__ == "__main__":
    main()
