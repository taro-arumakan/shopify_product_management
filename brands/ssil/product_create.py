import datetime
import logging
import zoneinfo
from brands.ssil.client import SsilClient, SsilClientMaterialOptionOnly

logging.basicConfig(level=logging.INFO)


def main():
    sheet_name = "GIFT"
    client = SsilClientMaterialOptionOnly()
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    client.sanity_check_sheet(sheet_name)
    scheduled_time = datetime.datetime(
        2025, 12, 4, 10, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    scgheduled_time = None
    client.process_sheet_to_products(sheet_name, scheduled_time=scheduled_time)


if __name__ == "__main__":
    main()
