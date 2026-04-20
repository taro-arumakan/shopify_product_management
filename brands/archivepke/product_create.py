import datetime
import logging
from brands.archivepke.client import ArchivepkeClient


logging.basicConfig(level=logging.INFO)


def main():
    handle_suffix = "26SS"

    sheet_name = "2026.04.22(26SS Collection)"
    client = ArchivepkeClient(
        product_sheet_start_row=3,
        remove_existing_new_product_indicators=True,
        products_season_tag=handle_suffix,
    )

    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 4, 22, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name, handle_suffix=handle_suffix)
    client.process_sheet_to_products(
        sheet_name=sheet_name,
        handle_suffix=handle_suffix,
        additional_tags=["New Arrival"],
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    main()
