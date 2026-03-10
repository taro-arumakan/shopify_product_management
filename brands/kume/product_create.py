import datetime
import logging
import zoneinfo
from brands.kume.client import KumeClient

logging.basicConfig(level=logging.INFO)


def main():
    sheet_name = "26SS_2次_3月16日"
    client = KumeClient(product_sheet_start_row=2)

    filter_func = lambda product_input: product_input["release_date"] == "2026-03-16"

    scheduled_time = datetime.datetime(
        2026, 3, 16, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name, product_inputs_filter_func=filter_func)

    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["26SS_2nd_DROP", "New Arrival"],
        scheduled_time=scheduled_time,
        product_inputs_filter_func=filter_func,
    )


if __name__ == "__main__":
    main()
