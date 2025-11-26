import datetime
import logging
from brands.blossom.client import BlossomClientClothes


logging.basicConfig(level=logging.INFO)


def main():
    client = BlossomClientClothes()
    sheet_name = "clothes(drop6)"

    client.sanity_check_sheet(sheet_name)

    # import zoneinfo

    # scheduled_time = datetime.datetime(
    #     2025, 10, 30, 12, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    # )
    # scheduled_time = None
    # client.process_product_info_list_to_products(
    #     product_info_list,
    #     additional_tags=["25_drop4", "New Arrival"],
    #     scheduled_time=scheduled_time,
    # )


if __name__ == "__main__":
    main()
