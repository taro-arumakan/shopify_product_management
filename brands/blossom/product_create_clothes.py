import datetime
import logging
from brands.blossom.client import BlossomClientClothes


logging.basicConfig(level=logging.DEBUG)


def main():
    client = BlossomClientClothes()
    sheet_names = ["clothes(drop11)", "clothes(drop12)", "clothes(jp exclusive)"]
    drop_tags = ["drop11", "drop12", "jp_exclusive"]

    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 1, 26, 18, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    for sheet_name, drop_tag in zip(sheet_names, drop_tags):
        client.sanity_check_sheet(sheet_name)

        client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = sheet_name == "clothes(drop11)"

        # client.process_sheet_to_products(
        #     sheet_name=sheet_name,
        #     additional_tags=[drop_tag, "New Arrival"],
        #     scheduled_time=scheduled_time,
        # )


if __name__ == "__main__":
    main()
