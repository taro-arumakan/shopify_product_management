import datetime
import logging
import zoneinfo

from brands.kume.client import KumeClient

logging.basicConfig(level=logging.INFO)


def create_26fw_2_0916():
    sheet_name = "26FW_(2)09.16"
    client = KumeClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag="26_0916_FW_2",
    )

    scheduled_time = datetime.datetime(
        2026, 9, 16, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival"],
        scheduled_time=scheduled_time,
    )


def create_26fw_3_0923():
    sheet_name = "26FW_(3)09.23"
    client = KumeClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag="26_0923_FW_3",
    )

    scheduled_time = datetime.datetime(
        2026, 9, 23, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival"],
        scheduled_time=scheduled_time,
    )


def main():
    create_26fw_2_0916()
    create_26fw_3_0923()


if __name__ == "__main__":
    main()
