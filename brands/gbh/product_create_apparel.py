import datetime
import logging
import zoneinfo
from brands.gbh.client import GbhClient

logging.basicConfig(level=logging.INFO)


def main():

    client = GbhClient()
    sheet_name = "APPAREL 25FW (WINTER 1次)"

    # client.sanity_check_sheet(sheet_name)
    product_info_list = client.product_info_list_from_sheet(sheet_name)
    product_info_list = [
        pi
        for pi in product_info_list
        if pi["title"] not in ["HIGH-NECK TOGGLE COAT", "SMART LONG GLOVES"]
    ]
    client.sanity_check_product_info_list(product_info_list)
    for product_info in product_info_list:
        client.create_a_product(product_info)
        client.process_product_images(product_info)
    client.update_stocks(product_info_list)
    scheduled_time = datetime.datetime(
        2025, 10, 27, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    client.publish_products(product_info_list, scheduled_time=scheduled_time)


if __name__ == "__main__":
    main()
