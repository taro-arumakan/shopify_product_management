from brands.gbh.client import GbhHomeClient, GbhClientColorOptionOnly


def process(client: GbhHomeClient, sheet_name):
    product_info_list = client.product_info_list_from_sheet(sheet_name)
    for product_info in product_info_list:
        product = client.product_by_title(product_info["title"])
        remarks = client.text_to_simple_richtext(product_info["product_remarks"])
        client.update_product_remarks_metafield(product["id"], remarks)


def main():
    client = GbhHomeClient()
    for sheet_name in ["bedding / ROBE (SIZE+COLOR)", "PILLOWCASE 修正"]:
        process(client, sheet_name)

    client = GbhClientColorOptionOnly()
    process(client, "bedding / ROBE (COLOR ONLY)")


if __name__ == "__main__":
    main()
