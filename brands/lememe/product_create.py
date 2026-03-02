import logging
from brands.lememe.client import LememeClient


logging.basicConfig(level=logging.INFO)


def main():
    client = LememeClient(product_sheet_start_row=1)
    sheet_name = "0305_RTW_spring"
    import datetime
    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 3, 5, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["26_Ready-to-Wear", "New Arrival"],
        scheduled_time=scheduled_time
    )


if __name__ == "__main__":
    main()
