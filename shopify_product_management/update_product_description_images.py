
import os
import string
from dotenv import load_dotenv
from shopify_graphql_client import ShopifyGraphqlClient
from shopify_product_management.google_utils import gdrive_service, drive_images_to_local
from shopify_product_management import utils

IMAGES_LOCAL_DIR = '/Users/taro/Downloads/rawrowr20250321/'
DUMMY_PRODUCT = 'gid://shopify/Product/8773753700593'
SHOPIFY_FILE_URL_PREFIX = 'https://cdn.shopify.com/s/files/1/0726/9187/6081/'

additional_punctuation_chars = '‘’“” '
punctuation_chrs = string.punctuation + additional_punctuation_chars
punctuation_translator = str.maketrans(punctuation_chrs, '_' * len(punctuation_chrs))

def list_folders(google_credential_path, parent_folder_id):
    service = gdrive_service(google_credential_path)
    query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(
            q=query,
            pageSize=1000,
            fields="files(id, name)",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
        ).execute()
    return results['files']

def main():
    cred = utils.credentials('rawrowr')
    parent_folder_id = '1ijec5ijfvFLvpzZGW7KmM7D0tQkUDky7'
    folders = list_folders(cred.google_credential_path, parent_folder_id=parent_folder_id)
    sgc = ShopifyGraphqlClient(cred.shop_name, cred.access_token)
    restart_from = "R TRUNK FRAME ep.3 88L _ 29'' 933"
    started = False
    for f in folders:
        dir_id = f['id']
        name = f['name']
        if name == restart_from:
            started = True
        if not started:
            continue
        if name != "R TRUNK FRAME ep.3 84L _ 20’’":
            prefix = name.translate(punctuation_translator)
            local_paths = drive_images_to_local(cred.google_credential_path, dir_id, IMAGES_LOCAL_DIR, download_filename_prefix=f'{prefix}_')
            if local_paths:
                product_id = sgc.product_id_by_title(name.replace('_', '/'))
                print(f'upload {len(local_paths)} images to {product_id}')
                sgc.upload_and_assign_description_images_to_shopify(product_id, local_paths, DUMMY_PRODUCT,
                                                                    'https://cdn.shopify.com/s/files/1/0726/9187/6081')

if __name__ == '__main__':
    main()
