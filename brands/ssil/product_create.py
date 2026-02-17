import datetime
import logging
import zoneinfo
from brands.ssil.client import SsilClientGoldLine

logging.basicConfig(level=logging.INFO)


def main():
    sheet_name = "GOLD PRODUCT"
    client = SsilClientGoldLine()
    # client.sanity_check_sheet(sheet_name)
    scheduled_time = datetime.datetime(
        2026, 2, 20, 12, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    client.process_sheet_to_products(
        sheet_name,
        scheduled_time=scheduled_time,
        additional_tags=["26_gold_line"],
        restart_at_product_title="[G]CIRCLE CHAIN R",
    )


if __name__ == "__main__":
    main()
