
import os
import string
from dotenv import load_dotenv
from shopify_product_management.google_utils import gdrive_service, get_drive_image_details, download_images_from_drive
from shopify_product_management.shopify_utils import product_id_by_title, upload_and_assign_description_images_to_shopify

load_dotenv(override=True)

SHOPNAME = 'rawrowr'

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
print(ACCESS_TOKEN)
GOOGLE_CREDENTIAL_PATH = os.getenv('GOOGLE_CREDENTIAL_PATH')
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
    parent_folder_id = '1ijec5ijfvFLvpzZGW7KmM7D0tQkUDky7'
    folders = list_folders(GOOGLE_CREDENTIAL_PATH, parent_folder_id=parent_folder_id)
    restart_from = "R TRUNK FRAME ep.3 88L _ 29'' 933"
    started = False
    for f in folders:
        dir_id = f['id']
        name = f['name']
        if name == restart_from:
            started = True
        if not started:
            continue
        prefix = name.translate(punctuation_translator)
        image_details = get_drive_image_details(GOOGLE_CREDENTIAL_PATH, dir_id, prefix)
        if image_details and name != "R TRUNK FRAME ep.3 84L / 20’’":
            print(f'going to process {name}:')
            # pprint.pprint(image_details, indent=8)
            product_id = product_id_by_title(SHOPNAME, ACCESS_TOKEN, name.replace('_', '/'))
            print(f'upload {len(image_details)} images to {product_id}')
            local_paths = download_images_from_drive(GOOGLE_CREDENTIAL_PATH, image_details, IMAGES_LOCAL_DIR)
            upload_and_assign_description_images_to_shopify(SHOPNAME, ACCESS_TOKEN, product_id, local_paths, DUMMY_PRODUCT,
                                                            'https://cdn.shopify.com/s/files/1/0726/9187/6081')

if __name__ == '__main__':
    main()
