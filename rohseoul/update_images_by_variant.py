import logging
import pprint
from dotenv import load_dotenv
from shopify_graphql_client import ShopifyGraphqlClient
import google_api_interface
import utils

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

UPLOAD_IMAGE_PREFIX = 'uplaod20250226_rohseoul_'
IMAGES_LOCAL_DIR = '/Users/taro/Downloads/rohseoul20250226/'

def process(sgc:ShopifyGraphqlClient, gai:google_api_interface.GoogleApiInterface, sku, folder_id):
    medias = sgc.medias_by_sku(sku)
    existing_ids = [m['id'] for m in medias]
    print(f'going to replace images of {sku} with {folder_id}')
    pprint.pprint(existing_ids)
    local_paths = gai.drive_images_to_local(folder_id, IMAGES_LOCAL_DIR, download_filename_prefix=f'{UPLOAD_IMAGE_PREFIX}_{sku}_')
    file_names = [path.rsplit('/', 1)[-1] for path in local_paths]
    mime_types = [f'image/{path.rsplit('.', 1)[-1]}' for path in local_paths]
    staged_targets = sgc.generate_staged_upload_targets(file_names, mime_types)
    logger.info(f'generated staged upload targets: {len(staged_targets)}')
    sgc.upload_images_to_shopify(staged_targets, local_paths, mime_types)
    product_id = sgc.product_id_by_sku(sku)
    logger.info(f"Images uploaded for {product_id}, going to remove existing and assign.")
    if medias:
        logger.info('media urls going to be removed:')
        pprint.pprint([m['image']['url'] for m in medias])
        sgc.remove_product_media_by_product_id(product_id, existing_ids)
    sgc.assign_images_to_product([target['resourceUrl'] for target in staged_targets],
                                 alts=file_names,
                                 product_id=product_id)
    variant_id = sgc.variant_id_by_sku(sku)
    uploaded_variant_media = sgc.media_by_product_id_by_file_name(product_id, file_names[0])
    sgc.assign_image_to_skus(product_id, uploaded_variant_media['id'], [variant_id])


def main():
    cred = utils.credentials('rohseoul')
    gai = google_api_interface.get('rohseoul')
    rows = gai.worksheet_rows(cred.google_sheet_id, '25SS 2차오픈(4월)(Summer 25)')
    sgc = ShopifyGraphqlClient(cred.shop_name, cred.access_token)
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
            drive_id = gai.drive_link_to_id(row[drive_link_column_index])
            if row[state_column_index] == 'CO' and drive_id and drive_id != '기존 상세페이지와 동일':
                logger.info(f'going to process: {sku} - {drive_id}')
                process(sgc, gai, sku, drive_id)


if __name__ == "__main__":
    main()
