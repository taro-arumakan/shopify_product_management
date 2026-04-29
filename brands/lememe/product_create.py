import logging
from brands.lememe.client import LememeClient


logging.basicConfig(level=logging.INFO)


def main():
    client = LememeClient(
        product_sheet_start_row=946,
        remove_existing_new_product_indicators=True,
        products_season_tag="26_hot_summer_bag",
    )
    sheet_name = "0501_bags_summer"
    import datetime
    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 5, 1, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(
        sheet_name,
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    main()
