from helpers.shopify_graphql_client import ShopifyGraphqlClient
from helpers.google_api_interface.interface import GoogleApiInterface

class Client(ShopifyGraphqlClient, GoogleApiInterface):
    def __init__(self, shop_name, access_token, google_credential_path, sheet_id=None):
        ShopifyGraphqlClient.__init__(self, shop_name=shop_name, access_token=access_token)
        GoogleApiInterface.__init__(self, google_credential_path=google_credential_path, sheet_id=sheet_id)

    def process_product_images(self, product_info, local_dir, local_prefix):
        product_id = self.product_id_by_title(product_info['title'])
        drive_links, skuss = self.populate_drive_ids_and_skuss(product_info)
        ress = []
        for index, (drive_id, skus) in enumerate(zip(drive_links, skuss)):
            local_paths = self.drive_images_to_local(drive_id, local_dir, f'{local_prefix}{skus[0]}')
            res = self.upload_and_assign_images_to_product(product_id, local_paths, remove_existings=index==0)
            ress.append(res)
            variant_media_id = res[-1]['productCreateMedia']['media'][0]['id']
            self.logger.info(f'assigning media {variant_media_id} to {skus}')
            variant_ids = [self.variant_id_by_sku(sku) for sku in skus]
            ress.append(self.assign_image_to_skus(product_id, variant_media_id, variant_ids))
        return ress
