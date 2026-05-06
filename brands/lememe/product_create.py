import logging
from brands.lememe.client import LememeClient, LememeClientApparel


logging.basicConfig(level=logging.INFO)


def main():
    client = LememeClientApparel(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=True,
        products_season_tag="2026_0506_RTW_summer",
    )
    sheet_name = "0506_RTW_summer"
    import datetime
    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 5, 6, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(
        sheet_name,
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    main()
