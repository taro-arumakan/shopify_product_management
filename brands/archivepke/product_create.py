import datetime
import logging
from brands.archivepke.client import ArchivepkeClient


logging.basicConfig(level=logging.INFO)


def main():
    handle_suffix = "26SS"

    sheet_name = "2026.03.05 (26SS COLLECTION 1ST)"
    client = ArchivepkeClient(product_sheet_start_row=3)

    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 3, 5, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name, handle_suffix=handle_suffix)
    client.process_sheet_to_products(
        sheet_name=sheet_name,
        handle_suffix=handle_suffix,
        additional_tags=["26SS", "New Arrival"],
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    main()
