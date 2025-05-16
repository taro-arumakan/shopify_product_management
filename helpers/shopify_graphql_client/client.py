import logging
import requests
from helpers.shopify_graphql_client.collection_queries import CollectionQueries
from helpers.shopify_graphql_client.inventory_management import InventoryManagement
from helpers.shopify_graphql_client.media_management import MediaManagement
from helpers.shopify_graphql_client.metafields_management import MetafieldsManagement
from helpers.shopify_graphql_client.product_attributes_management import (
    ProductAttributesManagement,
)
from helpers.shopify_graphql_client.product_create import ProductCreate
from helpers.shopify_graphql_client.product_queries import ProductQueries
from helpers.shopify_graphql_client.product_variants_to_products import (
    ProductVariantsToProducts,
)

logger = logging.getLogger(__name__)


class ShopifyGraphqlClient(
    CollectionQueries,
    InventoryManagement,
    MediaManagement,
    ProductAttributesManagement,
    ProductCreate,
    ProductQueries,
    ProductVariantsToProducts,
    MetafieldsManagement,
):
    def __init__(self, shop_name, access_token):
        self.shop_name = shop_name
        self.access_token = access_token
        self.base_url = (
            f"https://{shop_name}.myshopify.com/admin/api/2025-04/graphql.json"
        )

    def sanitize_id(self, identifier, prefix="Product"):
        if identifier.isnumeric():
            return f"gid://shopify/{prefix}/{identifier}"
        elif identifier.startswith("gid://"):
            assert (
                f"/{prefix}/" in identifier
            ), f"non-{prefix.lower()} gid was provided: {identifier}"
            return identifier
        else:
            raise ValueError(f"Invalid ID format: {identifier}")

    def run_query(self, query, variables=None, method="post"):
        headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        }
        data = {"query": query, "variables": variables}
        response = requests.post(self.base_url, headers=headers, json=data)
        res = response.json()
        if errors := res.get("errors"):
            raise RuntimeError(
                f"Error running the query: {errors}\n\n{query}\n\n{variables}"
            )
        if warnings := [
            r.get("warnings") for r in res.get("extensions", {}).get("search", [])
        ]:
            raise RuntimeError(
                f"Warning running the query: {warnings}\n\n{query}\n\n{variables}"
            )
        return res["data"]


def main():
    import logging

    logging.basicConfig(level=logging.INFO)
    from dotenv import load_dotenv

    load_dotenv(override=True)
    import os

    access_token = os.getenv("ACCESS_TOKEN")
    print(access_token)
    shop_name = "rawrowr"
    client = ShopifyGraphqlClient(shop_name, access_token)
    local_dir = r"/Users/taro/Downloads/rawrow_replace"
    paths = [
        os.path.join(local_dir, file)
        for file in os.listdir(local_dir)
        if file.endswith(".gif")
    ]
    import pprint

    res = client.replace_image_files(paths)
    pprint.pprint(res)


if __name__ == "__main__":
    main()
