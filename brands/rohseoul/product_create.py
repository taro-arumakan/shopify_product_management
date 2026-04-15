import datetime
import logging
import zoneinfo
from brands.rohseoul.client import RohseoulClient

logging.basicConfig(level=logging.INFO)


def main():
    handle_suffix = "26ss_2nd"

    client = RohseoulClient(
        product_sheet_start_row=2,
        remove_existing_new_product_indicators=True,
        products_season_tag=handle_suffix,
    )
    sheet_name = "26ss 2nd(NEW)"
    client.sanity_check_sheet(sheet_name, handle_suffix=handle_suffix)

    scheduled_time = datetime.datetime(
        2026, 4, 17, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.process_sheet_to_products(
        sheet_name=sheet_name,
        handle_suffix=handle_suffix,
        additional_tags=["New Arrival"],
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    main()
