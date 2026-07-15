import logging
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


def create_26ss_summer_bags():
    client = LememeClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag="2026_0716_bags_hot_summer",
    )
    sheet_name = "0716_bags_hot summer"

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


def main():
    create_26ss_summer_rtw()
    create_26ss_summer_slg()
    create_26ss_summer_bags()


if __name__ == "__main__":
    main()
