import datetime
import logging
import zoneinfo
from brands.ssil.client import SsilClientGoldLine

logging.basicConfig(level=logging.INFO)


def main():
    sheet_name = "gold確認必要"
    client = SsilClientGoldLine(product_sheet_start_row=1)
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    client.sanity_check_sheet(sheet_name)
    scheduled_time = datetime.datetime(
        2026, 2, 20, 12, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    scheduled_time = None
    client.process_sheet_to_products(
        sheet_name,
        scheduled_time=scheduled_time,
        additional_tags=["26_gold_line"],
    )


if __name__ == "__main__":
    main()
