import datetime
import logging
import zoneinfo
from brands.rohseoul.client import RohseoulClient

logging.basicConfig(level=logging.INFO)


def main():
    handle_suffix = "26_PRE-FALL_NEW"

    client = RohseoulClient(
        product_sheet_start_row=2,
        remove_existing_new_product_indicators=True,
        products_season_tag=handle_suffix,
    )
    sheet_name = "26 PRE-FALL(NEW)"
    client.sanity_check_sheet(sheet_name, handle_suffix=handle_suffix)

    scheduled_time = datetime.datetime(
        2026, 8, 14, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.process_sheet_to_products(
        sheet_name=sheet_name,
        handle_suffix=handle_suffix,
        additional_tags=["New Arrival"],
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    main()
