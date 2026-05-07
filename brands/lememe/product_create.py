import logging
from brands.lememe.client import LememeClient, LememeClientApparel


logging.basicConfig(level=logging.INFO)


def main():
    client = LememeClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=True,
        products_season_tag="2026_0515_bags",
    )
    sheet_name = "0515_bags"
    target_titles = {
        "Sac Lume",
        "Sac Clea",
        "Sac Romain Nylon",
        "Sac Benoit Black",
    }
    import datetime
    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 5, 15, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(
        sheet_name,
        product_inputs_filter_func=lambda pi: pi.get("title") in target_titles,
    )
    client.process_sheet_to_products(
        sheet_name,
        product_inputs_filter_func=lambda pi: pi.get("title") in target_titles,
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    main()
