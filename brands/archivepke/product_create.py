import datetime
import logging
from brands.archivepke.client import ArchivepkeClient


logging.basicConfig(level=logging.INFO)


def main():
    handle_suffix = "26-feb"

    sheet_name = "2026.02.02(core item new color)"
    client = ArchivepkeClient()

    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 2, 2, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name, handle_suffix=handle_suffix)
    client.process_sheet_to_products(
        sheet_name=sheet_name,
        handle_suffix=handle_suffix,
        additional_tags=["26_feb", "New Arrival"],
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    main()
