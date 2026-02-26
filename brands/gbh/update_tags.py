import logging
from brands.gbh.client import GbhClient, GbhClientColorOptionOnly

logging.basicConfig(level=logging.INFO)


def main():
    client = GbhClient(product_sheet_start_row=1)
    product_inputs = client.product_inputs_by_sheet_name(
        "26ss アパレルpre-spring어패럴프리스프링오픈(COLOR+SIZE)"
    )
    client = GbhClientColorOptionOnly(product_sheet_start_row=1)
    product_inputs += client.product_inputs_by_sheet_name(
        "26ss アパレルpre-spring어패럴프리스프링오픈(COLOR ONLY)"
    )
    q = " OR ".join(f"title:'{pi['title']}'" for pi in product_inputs)
    products = client.products_by_query(f"status:'ACTIVE' AND ({q})")
    for product in products:
        tags = product["tags"]
        tags += ["26_prespring", "Apparel"]
        client.update_product_tags(product["id"], ",".join(tags))


if __name__ == "__main__":
    main()
