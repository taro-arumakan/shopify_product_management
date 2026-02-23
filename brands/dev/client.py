import os
from brands.client.brandclientbase import BrandClientBase


def dev_client(base_brand_client: BrandClientBase):
    client = base_brand_client
    client.shop_name = "quickstart-6f3c9e4c"
    client.access_token = os.environ["quickstart-6f3c9e4c-ACCESS_TOKEN"]
    client.base_url = (
        f"https://{client.shop_name}.myshopify.com/admin/api/2025-10/graphql.json"
    )
    client.LOCATIONS = ["Shop location", "My Custom Location"]
    return client
