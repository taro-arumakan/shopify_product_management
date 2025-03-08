import logging
import os

from dotenv import load_dotenv
from google_utils import get_drive_image_details, get_sheet_index_by_title, get_link, download_images_from_drive, gspread_access, drive_link_to_id
from shopify_utils import (run_query, product_id_by_handle, product_id_by_title, medias_by_product_id,
                           generate_staged_upload_targets, upload_images_to_shopify,remove_product_media_by_product_id, assign_images_to_product,
                           assign_image_to_skus)

load_dotenv(override=True)
SHOPNAME = 'kumej'
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
print(ACCESS_TOKEN)
GOOGLE_CREDENTIAL_PATH = os.getenv('GOOGLE_CREDENTIAL_PATH')

UPLOAD_IMAGE_PREFIX = 'upload_20250307'
IMAGES_LOCAL_DIR = '/Users/taro/Downloads/gbh20250307/'
GSPREAD_ID = '1buFubQ6Ng4JzYn4JjTsv8SQ2J1Qgv1yyVrs4yQUHfE0'
SHEET_TITLE = '25ss'

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)


def upload_and_assign_images_to_product(product_id, drive_image_details):
    logger.info(f'number of images being downloaded/uploaded: {len(drive_image_details)}')
    file_names = [file_details['name'] for file_details in drive_image_details]
    local_paths = download_images_from_drive(GOOGLE_CREDENTIAL_PATH, drive_image_details, IMAGES_LOCAL_DIR)
    mime_types = [file_details['mimeType'] for file_details in drive_image_details]
    staged_targets = generate_staged_upload_targets(SHOPNAME, ACCESS_TOKEN, file_names, mime_types)
    logger.info(f'generated staged upload targets: {len(staged_targets)}')
    upload_images_to_shopify(staged_targets, local_paths, mime_types)
    logger.info(f"Images uploaded for {product_id}, going to remove existing and assign.")
    remove_product_media_by_product_id(SHOPNAME, ACCESS_TOKEN, product_id)
    assign_images_to_product(SHOPNAME, ACCESS_TOKEN,
                             [target['resourceUrl'] for target in staged_targets],
                             alts=[f['name'] for f in drive_image_details],
                             product_id=product_id)


def variant_by_sku(sku):
    query = """
    {
      productVariants(first: 10, query: "sku:'%s'") {
        nodes {
          id
          title
          product {
            id
          }
        }
      }
    }
    """ % sku
    response = run_query(SHOPNAME, ACCESS_TOKEN, query, {})
    json_data = response.json()
    return json_data['data']['productVariants']


def variant_id_for_sku(sku):
    json_data = variant_by_sku(sku)
    if len(json_data['nodes']) != 1:
        raise Exception(f"{'Multiple' if json_data['nodes'] else 'No'} variants found for {sku}: {json_data['nodes']}")
    return json_data['nodes'][0]['id']


def assign_image_to_skus_by_position(product_id, image_position, skus):
    logger.info(f'assigning a variant image to {skus}')
    variant_ids = [variant_id_for_sku(sku) for sku in skus]

    media_nodes = medias_by_product_id(SHOPNAME, ACCESS_TOKEN, product_id)
    media_id = media_nodes[image_position]['id']
    return assign_image_to_skus(SHOPNAME, ACCESS_TOKEN, product_id, media_id, variant_ids)


def product_media_by_sku(product_id, sku):      # TODO move to utils
    medias = medias_by_product_id(SHOPNAME, ACCESS_TOKEN, product_id)
    for media in medias:
        if any(s in media['alt'] for s in [f'{sku}_1.jpg', f'{sku}_00']):
            return media


def assign_variant_image_by_sku(skus):
    ''' Can be multiple SKUs of the same color in different sizes '''
    json_datas = [variant_by_sku(sku) for sku in skus]
    for sku, json_data in zip(skus, json_datas):
        if len(json_data['nodes']) != 1:
            raise Exception(f"{'Multiple' if json_data['nodes'] else 'No'} variants found for {sku}: {json_data['nodes']}")
    variants = [json_data['nodes'][0] for json_data in json_datas]
    product_ids = list(set(variant['product']['id'] for variant in variants))
    assert len(product_ids) == 1, f'Non-unique product {product_ids} for {skus}'
    product_id = product_ids[0]
    variant_ids = [variant['id'] for variant in variants]
    medias = list(
        filter(None, [product_media_by_sku(SHOPNAME, ACCESS_TOKEN, product_id, sku) for sku in skus]))
    if not medias:
        raise Exception(f'No media found for {skus}')
    media_ids = [media['id'] for media in medias]
    assert len(media_ids) == 1, f'Non-uqnique media {media_ids} for {skus}'
    return assign_image_to_skus(SHOPNAME, ACCESS_TOKEN, product_id, media_ids[0], variant_ids)


def process_product_images_to_shopify(image_prefix, product_title, drive_ids, skuss):
    """
    Processes and uploads images for a product to Shopify, associating them with
    specific SKUs based on their positions within provided Google Drive folders.

    :param image_prefix: A prefix to be added to each image file name during processing.
    :param product_title: The title of the product in Shopify. Used to retrieve the product ID.
    :param drive_ids: A list of Google Drive folder IDs, each containing images for different color variants of the product.
    :param skuss: A nested list of SKUs. Each inner list corresponds to a Google Drive folder and contains SKUs for different sizes of the same color variant.

    Example:
    image_prefix = '20240901_sample_upload_'
    product_title = 'Twisted Neck Superfine Merino Wool Cardigan'
    drive_ids = [
        '1qEME0URUWETd_fepr3KJFSz2EhXCxjoJ',
        '1ACt4g7tqigsmXYemUCc9KnDynW20E5Iz',
        '15VwlvmnC7EBmOZaslyMq40KyHXcWt63g'
    ]
    skuss = [
        ['KM-24FW-SW01-IV-S', 'KM-24FW-SW01-IV-M'],
        ['KM-24FW-SW01-MT-S', 'KM-24FW-SW01-MT-M'],
        ['KM-24FW-SW01-DBR-S', 'KM-24FW-SW01-DBR-M']
    ]
    """
    if SHOPNAME in ['rohseoul', 'archive-epke']:
        product_handle = '-'.join(list(map(str.lower, product_title.replace(')', '').replace('(', '').split(' '))) + ['25ss'])
        logger.info(f'product_handle: {product_handle}')
        product_id = product_id_by_handle(SHOPNAME, ACCESS_TOKEN, product_handle)
    elif SHOPNAME in ['gbhjapan']:
        product_handle = '-'.join(list(map(str.lower, product_title.replace(')', '').replace('(', '').split(' '))) + ['25', 'spring'])
        product_id = product_id_by_handle(SHOPNAME, ACCESS_TOKEN, product_handle)
    else:
        product_id = product_id_by_title(SHOPNAME, ACCESS_TOKEN, product_title)

    drive_image_details = []
    variant_image_positions = []

    for drive_id, skus in zip(drive_ids, skuss):
        variant_image_positions.append(len(drive_image_details))
        drive_image_details += get_drive_image_details(GOOGLE_CREDENTIAL_PATH, drive_id, skus[0], image_prefix)

    logger.debug(f"Drive Image Details: {drive_image_details}")

    upload_and_assign_images_to_product(product_id, drive_image_details)

    for skus, image_position in zip(skuss, variant_image_positions):
        assign_image_to_skus_by_position(product_id, image_position, skus)


def products_info_from_sheet(shop_name, sheet_id, sheet_index=0):
    worksheet = gspread_access(GOOGLE_CREDENTIAL_PATH).open_by_key(sheet_id).get_worksheet(sheet_index)
    rows = worksheet.get_all_values()

    # start_row 1 base, columns are 0 base
    if shop_name == 'kumej':
        title_column_index = 2
        color_column_index = 15
        sku_column_index = 18
        link_column_index = 16
        start_row = 49
    elif shop_name == 'gbhjapan':
        title_column_index = 5
        color_column_index = 6
        sku_column_index = 8
        link_column_index = 14
        start_row = 3
    elif shop_name == 'alvanas':
        title_column_index = 1
        color_column_index = 9
        sku_column_index = 12
        link_column_index = 10
        start_row = 2
    elif shop_name == 'rawrowr':
        title_column_index = 1
        color_column_index = 12
        sku_column_index = 16
        link_column_index = 14
        start_row = 3
    elif shop_name == 'rohseoul':
        state_column_index = 0
        title_column_index = 4
        color_column_index = 9
        sku_column_index = 5
        link_column_index = 15
        start_row = 3
    elif shop_name == 'archive-epke':
        title_column_index = 3
        color_column_index = 8
        sku_column_index = 4
        link_column_index = 14
        start_row = 3
    else:
        raise RuntimeError(f'unknown shop {shop_name}')

    products = []
    current_product_title = ''

    for row_num, row in enumerate(rows[start_row - 1:]):  # Skip headers
        if SHOPNAME == 'rohseoul':
            state = row[state_column_index].strip()
            if state != 'NEW':
                logger.info(f'skipping row {row_num}')
                continue
        elif SHOPNAME == 'kumej':
            release = row[1]
            if release.startswith('3/31'):
                logger.info(f'stop processing at {row_num}')
                break
        sku = row[sku_column_index].strip()
        if not sku:
            break
        product_title = row[title_column_index].strip()
        if not product_title:
            product_title = current_product_title
        if product_title != current_product_title:
            products.append(dict(product_title=product_title,
                                 skuss=[],
                                 links=[]))
            current_product_title = product_title
            current_color = ''
        color = row[color_column_index].strip()
        if not color:
            color = current_color
        if color != current_color:
            current_color = color
            products[-1]['skuss'].append([sku])
        else:
            products[-1]['skuss'][-1].append(sku)
        logger.info(f'retrieving link for {product_title}')
        link = get_link(GOOGLE_CREDENTIAL_PATH, sheet_id, SHEET_TITLE, row, start_row + row_num, link_column_index)
        if link and link != 'no image':
            if not link.startswith('http'):
                logger.exception(f'\n!!! malformed URL: {link} !!!\n')
            products[-1]['links'].append(link)
    return products


def main():
    image_prefix = UPLOAD_IMAGE_PREFIX
    sheet_index = get_sheet_index_by_title(GOOGLE_CREDENTIAL_PATH, GSPREAD_ID, SHEET_TITLE)
    logger.info(f'sheet index of {SHEET_TITLE} is {sheet_index}')
    product_details = products_info_from_sheet(shop_name=SHOPNAME, sheet_id=GSPREAD_ID, sheet_index=sheet_index)

    reprocess_titles, reprocess_skus = [], []
    reprocess_from_sku = ''

    if reprocess_from_sku:
        import itertools
        all_skus = list(itertools.chain(sku for pr in product_details for skus in pr['skuss'] for sku in skus))
        logger.info(all_skus)
    for pr in product_details:
        if ((all((not(reprocess_skus), not(reprocess_titles))) or
            any(sku in skus for sku in reprocess_skus for skus in pr['skuss']) or
            pr['product_title'] in reprocess_titles) and
            (not reprocess_from_sku or reprocess_from_sku and any(all_skus.index(sku) >= all_skus.index(reprocess_from_sku) for skus in pr['skuss'] for sku in skus))):
            drive_ids = list(dict.fromkeys(drive_link_to_id(pp) for pp in pr['links']).keys())
            logger.info(f'''
                  processing {pr['product_title']}
                  SKUs: {pr['skuss']}
                  Folders: {drive_ids}
                  ''')
            process_product_images_to_shopify(
                image_prefix, pr['product_title'], drive_ids, pr['skuss'])

if __name__ == "__main__":
    main()
