import datetime
import logging
import zoneinfo

from brands.kume.client import KumeClient

logging.basicConfig(level=logging.INFO)


def create_26fw_4_1001():
    sheet_name = "26FW_(4)10.01"
    client = KumeClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag="26_1001_FW_4",
    )

    scheduled_time = datetime.datetime(
        2026, 10, 1, 11, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["26FW"],
        scheduled_time=scheduled_time,
    )


def create_26fw_5_1008():
    sheet_name = "26FW_(5)10.08"
    client = KumeClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag="26_1008_FW_5",
    )

    scheduled_time = datetime.datetime(
        2026, 10, 8, 11, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["26FW"],
        scheduled_time=scheduled_time,
        restart_at_product_title="Wool Relaxed V-Neck Sweater, Light Blue",
    )


def main():
    # create_26fw_4_1001()
    create_26fw_5_1008()


if __name__ == "__main__":
    main()
