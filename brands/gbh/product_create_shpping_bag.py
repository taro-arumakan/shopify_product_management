import datetime
import logging
import zoneinfo
from brands.gbh.client import GbhClientSizeOptionOnly

logging.basicConfig(level=logging.INFO)


def main():

    client = GbhClientSizeOptionOnly()
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    sheet_name = "ショッパー登録(쇼핑백 등록시트)"

    client.sanity_check_sheet(sheet_name)

    scheduled_time = datetime.datetime(
        2025, 11, 14, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )
    scheduled_time = None

    client.process_sheet_to_products(
        sheet_name, additional_tags=["New Arrival"], scheduled_time=scheduled_time
    )


if __name__ == "__main__":
    main()
