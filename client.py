from shopify_graphql_client import ShopifyGraphqlClient
from google_api_interface.interface import GoogleApiInterface

class Client(ShopifyGraphqlClient, GoogleApiInterface):
    def __init__(self, shop_name, access_token, google_credential_path, sheet_id=None):
        ShopifyGraphqlClient.__init__(self, shop_name=shop_name, access_token=access_token)
        GoogleApiInterface.__init__(self, google_credential_path=google_credential_path, sheet_id=sheet_id)
