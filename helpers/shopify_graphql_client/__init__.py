from helpers.shopify_graphql_client.client import ShopifyGraphqlClient

def get(shop_name):
    from utils import credentials
    cred = credentials(shop_name)
    return ShopifyGraphqlClient(cred.shop_name, cred.access_token)
