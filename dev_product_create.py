import datetime
import logging
import os

logging.basicConfig(level=logging.INFO)

from brands.apricotstudios.client import ApricotStudiosClient
from brands.blossom.client import BlossomClientClothes
from brands.rohseoul.client import RohseoulClient


def main():
    client = ApricotStudiosClient(
        9367616946431,
        product_detail_images_folder_id="1fCXufym34XgTt80wq0ADVrQ-3SWXZQIZ",
    )
    client.shop_name = "quickstart-6f3c9e4c"
    client.access_token = os.environ["quickstart-6f3c9e4c-ACCESS_TOKEN"]
    client.base_url = (
        f"https://{client.shop_name}.myshopify.com/admin/api/2025-10/graphql.json"
    )
    client.LOCATIONS = ["Shop location", "My Custom Location"]

    sheet_name = "[Spring_1st] 2/25"

    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 2, 25, 10, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.process_sheet_to_products(
        sheet_name=sheet_name,
        restart_at_product_title="Soy Ringer T-shirt",
        additional_tags=["26_spring_1st", "New Arrival"],
        scheduled_time=scheduled_time,
    )


if __name__ == "__main__":
    main()
