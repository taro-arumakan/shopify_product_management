import logging
import os
import pprint
from dotenv import load_dotenv
from shopify_utils import medias_by_sku, generate_staged_upload_targets, upload_images_to_shopify, remove_product_media_by_product_id, product_id_by_sku, assign_images_to_product, assign_image_to_skus, variant_id_by_sku, product_media_by_file_name
from google_utils import get_drive_image_details, download_images_from_drive, worksheet_rows, drive_link_to_id


logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)


load_dotenv(override=True)
SHOPNAME = 'rohseoul'
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
GOOGLE_CREDENTIAL_PATH = os.getenv('GOOGLE_CREDENTIAL_PATH')
UPLOAD_IMAGE_PREFIX = 'uplaod20250226_rohseoul_'
IMAGES_LOCAL_DIR = '/Users/taro/Downloads/rohseoul20250226/'

SHEET_ID = '19V9vmTK8VmyNWjz6jgnbfO4nm88XkOrNRvcb7a04ydI'
SHEET_TITLE = '25SS'

def process(sku, folder_id):
    drive_image_details = get_drive_image_details(GOOGLE_CREDENTIAL_PATH, folder_id, download_filename_prefix=f'{UPLOAD_IMAGE_PREFIX}_{sku}_')
    medias = medias_by_sku(SHOPNAME, ACCESS_TOKEN, sku)
    existing_ids = [m['id'] for m in medias]
    print(f'going to replace images of {sku} with {folder_id}')
    pprint.pprint(existing_ids)
    local_paths = download_images_from_drive(GOOGLE_CREDENTIAL_PATH, drive_image_details, IMAGES_LOCAL_DIR)
    file_names = [file_details['name'] for file_details in drive_image_details]
    mime_types = [file_details['mimeType'] for file_details in drive_image_details]
    staged_targets = generate_staged_upload_targets(SHOPNAME, ACCESS_TOKEN, file_names, mime_types)
    logger.info(f'generated staged upload targets: {len(staged_targets)}')
    upload_images_to_shopify(staged_targets, local_paths, mime_types)
    product_id = product_id_by_sku(SHOPNAME, ACCESS_TOKEN, sku)
    logger.info(f"Images uploaded for {product_id}, going to remove existing and assign.")
    if medias:
        logger.info('media urls going to be removed:')
        pprint.pprint([m['image']['url'] for m in medias])
        remove_product_media_by_product_id(SHOPNAME, ACCESS_TOKEN, product_id, existing_ids)
    assign_images_to_product(SHOPNAME, ACCESS_TOKEN,
                                [target['resourceUrl'] for target in staged_targets],
                                alts=[f['name'] for f in drive_image_details],
                                product_id=product_id)
    variant_id = variant_id_by_sku(SHOPNAME, ACCESS_TOKEN, sku)
    uploaded_variant_media = product_media_by_file_name(SHOPNAME, ACCESS_TOKEN, product_id, file_names[0])
    assign_image_to_skus(SHOPNAME, ACCESS_TOKEN, product_id, uploaded_variant_media['id'], [variant_id])


def main():
    rows = worksheet_rows(GOOGLE_CREDENTIAL_PATH, SHEET_ID, SHEET_TITLE)
    sku_column_index = 5
    state_column_index = 0
    drive_link_column_index = 15
    restart_from_sku = 'JLL00CC8SBK'
    started = False
    for row in rows:
        sku = row[sku_column_index]
        if sku == restart_from_sku:
            started = True
        if started:
            drive_id = drive_link_to_id(row[drive_link_column_index])
            if row[state_column_index] == 'CO' and drive_id and drive_id != '기존 상세페이지와 동일':
                logger.info(f'going to process: {sku} - {drive_id}')
                process(sku, drive_id)


if __name__ == "__main__":
    main()
