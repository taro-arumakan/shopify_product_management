from shopify_graphql_client import ShopifyGraphqlClient
from google_api_interface.interface import GoogleApiInterface

class Client(ShopifyGraphqlClient, GoogleApiInterface):
    def __init__(self, shop_name, access_token, google_credential_path, sheet_id=None):
        ShopifyGraphqlClient.__init__(self, shop_name=shop_name, access_token=access_token)
        GoogleApiInterface.__init__(self, google_credential_path=google_credential_path, sheet_id=sheet_id)

    def process_product_images(self, product_info, local_dir, local_prefix):
        product_id = self.product_id_by_title(product_info['title'])
        local_paths = []
        drive_links, skuss = self.populate_drive_ids_and_skuss(product_info)
        ress = []
        for drive_id, skus in zip(drive_links, skuss):
            local_paths += self.drive_images_to_local(drive_id, local_dir, f'{local_prefix}{skus[0]}')
            res = self.upload_and_assign_images_to_product(product_id, local_paths)
            ress.append(res)
            variant_media_id = res[0]['media']['id']
            ress.append(self.assign_image_to_skus(product_id, variant_media_id, skus))
        return ress
