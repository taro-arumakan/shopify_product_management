import string
import utils
from brands.rohseoul.product_create import get_description_html


def product_info_lists_from_sheet(
    gai: utils.Client, sheet_id, sheet_name, handle_suffix
):
    start_row = 2
    column_product_attrs = dict(
        title=string.ascii_lowercase.index("d"),
        status=string.ascii_lowercase.index("a"),
        release_date=string.ascii_lowercase.index("c"),
        collection=string.ascii_lowercase.index("f"),
        category=string.ascii_lowercase.index("g"),
        description=string.ascii_lowercase.index("r"),
        size_text=string.ascii_lowercase.index("u"),
        material=string.ascii_lowercase.index("v"),
        made_in=string.ascii_lowercase.index("w"),
    )
    column_variant_attrs = {"カラー": string.ascii_lowercase.index("i")}
    column_variant_attrs.update(
        sku=string.ascii_lowercase.index("e"),
        price=string.ascii_lowercase.index("l"),
        stock=string.ascii_lowercase.index("m"),
        drive_link=string.ascii_lowercase.index("p"),
    )
    return gai.to_products_list(
        sheet_id,
        sheet_name,
        start_row,
        column_product_attrs,
        column_variant_attrs,
        handle_suffix=handle_suffix,
    )


def main():
    client = utils.client("rohseoul")
    product_info_list = product_info_lists_from_sheet(
        client, client.sheet_id, "9/27 発売 24FW 新作", ""
    )

    for product_info in product_info_list:
        if product_info["title"] in [
            "Pulpy crossbody bag Suede",
        ]:
            description_html = get_description_html(
                client,
                product_info["description"],
                product_info["material"],
                product_info["size_text"],
                product_info["made_in"],
            )
            product_id = client.product_id_by_handle(product_info["handle"])
            print(description_html)
            print(product_info["handle"])
            print(product_id)
            client.update_product_description(product_id, description_html)


if __name__ == "__main__":
    main()
