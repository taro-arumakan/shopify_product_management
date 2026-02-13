import datetime
import logging
import zoneinfo
from brands.kume.client import KumeClient

logging.basicConfig(level=logging.INFO)


def main():
    sheet_name = "26SS_1次_2月23日"
    client = KumeClient()

    filter_func = lambda product_input: product_input["release_date"] == "2026-02-23"

    scheduled_time = datetime.datetime(
        2026, 2, 23, 12, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name, product_inputs_filter_func=filter_func)

    client.process_sheet_to_products(
        sheet_name,
        scheduled_time=scheduled_time,
        product_inputs_filter_func=filter_func,
    )


if __name__ == "__main__":
    main()
