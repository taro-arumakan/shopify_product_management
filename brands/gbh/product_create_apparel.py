import datetime
import logging
import zoneinfo
from brands.gbh.client import GbhClient, GbhClientColorOptionOnly

logging.basicConfig(level=logging.INFO)


def create_26ss_color_size():
    client = GbhClient()
    sheet_name = "26ss アパレルpre-spring어패럴프리스프링오픈(COLOR+SIZE)"
    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(sheet_name, additional_tags=["New Arrival"])

def create_26ss_color_only():
    client = GbhClientColorOptionOnly()
    sheet_name = "26ss アパレルpre-spring어패럴프리스프링오픈(COLOR ONLY)"
    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(sheet_name, additional_tags=["New Arrival"])

def archive_products():
    client = GbhClient()
    titles = [
        "WIDE CINCH-BACK JEAN",
        "FAUX SUEDE BOMBER",
        "TWIST BELT",
        "COTTON RIB SOCKS"
    ]
    for title in titles:
        product = client.product_by_title(title)
        client.archive_product(product)

def main():

    # client = GbhClient()
    # sheet_name = "26ss アパレルpre-spring어패럴프리스프링오픈(COLOR+SIZE)"

    # """
    # From 25 Winter onward, only keep the products released in recent one year.
    # e.g. archive 24FW before releasing 25FW.
    # Refer to archive_products.py.
    # """

    # client.sanity_check_sheet(sheet_name)

    # scheduled_time = datetime.datetime(
    #     2025, 11, 14, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    # )

    # client.process_sheet_to_products(
    #     sheet_name,
    #     additional_tags=["New Arrival"],
    #     scheduled_time=scheduled_time)

    archive_products()
    create_26ss_color_only()
    create_26ss_color_size()


if __name__ == "__main__":
    main()
