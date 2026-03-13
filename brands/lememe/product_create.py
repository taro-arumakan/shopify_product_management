import logging
from brands.lememe.client import LememeClientApparel


logging.basicConfig(level=logging.INFO)


def main():
    client = LememeClientApparel(product_sheet_start_row=1)
    sheet_name = "0305_RTW_spring"
    import datetime
    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 3, 5, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    scheduled_time = None
    product_inputs = client.product_inputs_by_sheet_name(sheet_name)
    products = client.products_by_query(
        " OR ".join(f"title:'{pi['title']}'" for pi in product_inputs)
    )
    for product in products:
        client.archive_product(product)

    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["26_Ready-to-Wear", "New Arrival"],
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    main()
