import datetime
import logging
import zoneinfo
from brands.ssil.client import SsilClientGoldLine

logging.basicConfig(level=logging.INFO)


def main():
    sheet_name = "GOLD0303"
    client = SsilClientGoldLine(product_sheet_start_row=1)

    client.sanity_check_sheet(sheet_name)
    scheduled_time = datetime.datetime(
        2026, 3, 19, 12, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    client.process_sheet_to_products(
        sheet_name,
        scheduled_time=scheduled_time,
        additional_tags=["GOLD0_303", "New Arrival"],
    )


if __name__ == "__main__":
    main()
