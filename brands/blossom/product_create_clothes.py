import datetime
import logging
from brands.blossom.client import BlossomClientClothes


logging.basicConfig(level=logging.DEBUG)


def main():
    client = BlossomClientClothes()
    sheet_name = "clothes(drop8)"

    client.sanity_check_sheet(sheet_name)

    import zoneinfo

    scheduled_time = datetime.datetime(
        2025, 12, 25, 11, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False

    client.process_sheet_to_products(
        sheet_name=sheet_name,
        additional_tags=["25_drop8", "New Arrival"],
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    main()
