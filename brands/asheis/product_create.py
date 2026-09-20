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
    sheet_names = [
        # "【10デリ_1】Products Master",
        "【10デリ_2】Products Master"
    ]
    additional_tags = [
        # "26_oct_1",
        "26_oct_2"
    ]
    scheduled_times = [
        # datetime.datetime(2026, 9, 30, 12, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")),
        datetime.datetime(2026, 10, 14, 12, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")),
    ]

    # for sheet_name in sheet_names:
    #     client.sanity_check_sheet(sheet_name)

    for sn, at, st in zip(sheet_names, additional_tags, scheduled_times):
        client.process_sheet_to_products(
            sn,
            additional_tags=[at],
            scheduled_time=st,
            restart_at_product_title="WOOL BLEND CROPPED JACKET",
        )


if __name__ == "__main__":
    main()
