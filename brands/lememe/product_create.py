import logging

from numpy import full
from brands.lememe.client import LememeClient, LememeClientApparel


logging.basicConfig(level=logging.INFO)


def create_26ss_summer_rtw():
    client = LememeClientApparel(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=True,
        products_season_tag="2026_0716_rtw_hot_summer",
    )
    sheet_name = "0716_rtw_hot summer"

    import datetime
    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 7, 15, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival"],
        scheduled_time=scheduled_time,
    )


def create_26ss_summer_slg():
    client = LememeClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag="2026_0716_slg_hot_summer",
    )
    sheet_name = "0716_slg_hot summer"

    import datetime
    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 7, 15, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival"],
        scheduled_time=scheduled_time,
    )


def create_26_0901_fall_bags():
    client = LememeClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag="2026_0901_bags_fall",
    )
    sheet_name = "0901_bags_fall"

    import datetime
    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 9, 1, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    filter_func = lambda product_input: str(product_input.get("release_date", "")) in (
        "9/1",
        "2026-09-01",
    )

    client.sanity_check_sheet(sheet_name, product_inputs_filter_func=filter_func)
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["New Arrival"],
        scheduled_time=scheduled_time,
        product_inputs_filter_func=filter_func
    )


def main():
    create_26_0901_fall_bags()


if __name__ == "__main__":
    main()
