import datetime
import logging
import zoneinfo
from brands.asheis.client import AsheisClient

logging.basicConfig(level=logging.DEBUG)


def main():
    client = AsheisClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag="26FW",
    )
    sheet_names = ["【0924デリ】Products Master"]
    additional_tags = ["26_sep"]
    scheduled_times = [
        datetime.datetime(2026, 9, 24, 12, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")),
    ]

    for sheet_name in sheet_names:
        client.sanity_check_sheet(sheet_name)

    for sn, at, st in zip(sheet_names, additional_tags, scheduled_times):
        client.process_sheet_to_products(
            sn,
            additional_tags=[at],
            scheduled_time=st,
        )


if __name__ == "__main__":
    main()
