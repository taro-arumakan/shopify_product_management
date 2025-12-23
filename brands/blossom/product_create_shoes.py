from datetime import datetime
import logging
from brands.blossom.client import BlossomClientShoes

logging.basicConfig(level=logging.INFO)


def main():
    client = BlossomClientShoes()
    sheet_name = "shoes(drop7)"
    client.sanity_check_sheet(sheet_name)

    import zoneinfo

    scheduled_time = datetime.datetime(
        2025, 12, 25, 11, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False

    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["25_drop8", "New Arrival"],
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    main()
