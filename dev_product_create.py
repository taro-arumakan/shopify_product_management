import logging

logging.basicConfig(level=logging.INFO)

import os
from brands.rohseoul.client import RohseoulClient


def main():
    client = RohseoulClient()
    client.shop_name = "quickstart-6f3c9e4c"
    client.access_token = os.environ["quickstart-6f3c9e4c-ACCESS_TOKEN"]
    client.base_url = (
        f"https://{client.shop_name}.myshopify.com/admin/api/2025-10/graphql.json"
    )
    client.LOCATIONS = ["Shop location", "My Custom Location"]

    client.process_sheet_to_products(
        sheet_name="25FW WINTER - copy", handle_suffix="25-fall"
    )


if __name__ == "__main__":
    main()
