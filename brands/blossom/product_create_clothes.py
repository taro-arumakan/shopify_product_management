import datetime
import logging
from brands.blossom.client import BlossomClientClothes


logging.basicConfig(level=logging.INFO)


def main():
    client = BlossomClientClothes()
    sheet_name = "clothes(drop4) のclone"
    client.sanity_check_sheet(sheet_name)

    import zoneinfo

    scheduled_time = datetime.datetime(
        2025, 10, 30, 12, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    client.process_sheet_to_products(sheet_name, scheduled_time=scheduled_time)


if __name__ == "__main__":
    main()
