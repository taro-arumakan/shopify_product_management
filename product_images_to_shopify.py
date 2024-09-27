import io
import logging
import os
import re
import time
import requests
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

load_dotenv(override=True)
SHOPNAME = os.getenv('SHOPNAME')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
GOOGLE_CREDENTIAL_PATH = os.getenv('GOOGLE_CREDENTIAL_PATH')

UPLOAD_IMAGE_PREFIX = 'upload_20240925_'
IMAGES_LOCAL_DIR = '/Users/taro/Downloads/gbh20240925/'
GSPREAD_ID = '10L3Rqrno6f4VZvJRHC5dvuZgVxKzTo3wK9KvB210JC0'
SHEET_TITLE = '9月27日 AW APPAREL(2)'

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

google_credentials = None


def authenticate_google_api():
    # Authenticate to Google API using Service Account
    global google_credentials
    if not google_credentials:
        google_credentials = Credentials.from_service_account_file(
            GOOGLE_CREDENTIAL_PATH,
            scopes=['https://www.googleapis.com/auth/drive',
                    'https://www.googleapis.com/auth/spreadsheets']
        )
    return google_credentials


_gdrive_service = None


def gdrive_service():
    global _gdrive_service
    if not _gdrive_service:
        _gdrive_service = build('drive', 'v3', credentials=authenticate_google_api())
    return _gdrive_service


def gspread_access():
    creds = authenticate_google_api()
    return gspread.authorize(creds)


_gsheet_service = None


def gsheet_service():
    global _gsheet_service
    if not _gsheet_service:
        _gsheet_service = build('sheets', 'v4', credentials=authenticate_google_api())
    return _gsheet_service


def run_query(query, variables=None, method='post', resource='graphql'):
    url = f'https://{SHOPNAME}.myshopify.com/admin/api/2024-07/{resource}.json'
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    data = {
        "query": query,
        "variables": variables
    }
    return requests.post(url, headers=headers, json=data)


def natural_compare(k):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    return [convert(c) for c in re.split('([0-9]+)', k)]


def get_drive_image_details(folder_id, sku, image_prefix):
    service = gdrive_service()
    results = service.files().list(
        q=f"'{folder_id}' in parents", pageSize=1000).execute()
    items = results.get('files', [])

    # Sort files using natural order
    items.sort(key=lambda f: natural_compare(f['name']))

    res = []
    sequence = 0

    for item in items:
        if item['mimeType'].startswith('image/'):
            file_metadata = {
                'name': f"{image_prefix}_{sku}_{str(sequence).zfill(2)}_{item['name']}",
                'mimeType': item['mimeType'],
                'id': item['id'],
                # 'downloadUrl': f"https://www.googleapis.com/drive/v3/files/{item['id']}?alt=media"
            }
            res.append(file_metadata)
            sequence += 1
    return res


def generate_staged_upload_targets(files):
    query = """
    mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
      stagedUploadsCreate(input: $input) {
        stagedTargets {
          url
          resourceUrl
          parameters {
            name
            value
          }
        }
        userErrors {
          field
          message
        }
      }
    }
    """

    variables = {
        "input": [{
            "resource": "IMAGE",
            "filename": file['name'],
            "mimeType": file['mimeType'],
            "httpMethod": "POST",
        } for file in files]
    }

    response = run_query(query, variables)
    return response.json()['data']['stagedUploadsCreate']['stagedTargets']


def download_file_from_drive(file_id, destination_path):
    service = gdrive_service()
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        logger.debug(f"Download {int(status.progress() * 100)}%.")


def upload_images_to_shopify(staged_targets, file_details):
    for target, file_details in zip(staged_targets, file_details):
        logger.info(f'  processing {file_details['name']}')

        payload = {
            'Content-Type': file_details['mimeType'],
            'success_action_status': '201',
            'acl': 'private',
        }
        payload.update({param['name']: param['value']
                       for param in target['parameters']})
        local_path = os.path.join(IMAGES_LOCAL_DIR, file_details['name'])
        if not os.path.exists(local_path):
            logger.debug(f'  starting download of {file_details['name']}')
            download_file_from_drive(file_details['id'], local_path)

        with open(local_path, 'rb') as f:
            logger.debug(f'  starting upload of {file_details['name']}')
            response = requests.post(target['url'],
                                     files={'file': (file_details['name'], f)},
                                     data=payload)
        logger.debug(f"upload response: {response.status_code}")
        if response.status_code != 201:
            logger.exception(f'\n\n!!! upload failed !!!\n\n{
                             file_details}:\n{target}\n\n{response.text}\n\n')


def product_id_by_title(title):
    query = """
    query productsByQuery($query_string: String!) {
      products(first: 10, query: $query_string, sortKey: TITLE) {
        nodes {
          id
          title
        }
      }
    }
    """
    variables = {
        "query_string": f"Title: '{title}'"
    }
    response = run_query(query, variables)
    json_data = response.json()

    products = json_data['data']['products']['nodes']
    if len(products) != 1:
        raise Exception(f"Multiple products found for {title}: {products}")
    return products[0]['id']


def remove_product_media_by_product_id(product_id):
    media_nodes = product_media_status(product_id)
    media_ids = [node['id'] for node in media_nodes]

    if not media_ids:
        logger.debug(f"Nothing to delete for {product_id}")
        return True

    logger.info(f"Going to delete {media_ids} from {product_id}")

    query = """
    mutation deleteProductMedia($productId: ID!, $mediaIds: [ID!]!) {
      productDeleteMedia(productId: $productId, mediaIds: $mediaIds) {
        deletedMediaIds
        product {
          id
        }
        mediaUserErrors {
          code
          field
          message
        }
      }
    }
    """

    variables = {
        "productId": product_id,
        "mediaIds": media_ids
    }
    response = run_query(query, variables)
    logger.debug(response.json())
    return response


def assign_images_to_product(resource_urls, alts, product_id):
    mutation_query = """
    mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
      productCreateMedia(media: $media, productId: $productId) {
        media {
          alt
          mediaContentType
          status
        }
        userErrors {
          field
          message
        }
        product {
          id
          title
        }
      }
    }
    """

    medias = [{
        "originalSource": url,
        "alt": alt,
        "mediaContentType": "IMAGE"
    } for url, alt in zip(resource_urls, alts)]

    variables = {
        "media": medias,
        "productId": product_id
    }

    response = run_query(mutation_query, variables)
    json_data = response.json()

    logger.debug("Initial media status:")
    logger.debug(json_data)

    if json_data['data']['productCreateMedia']['userErrors']:
        raise Exception(f"Error during media creation: {
                        json_data['data']['productCreateMedia']['userErrors']}")

    status = wait_for_media_processing_completion(product_id)
    if not status:
        raise Exception("Error during media processing")


def product_media_status(product_id):
    query = """
    query ProductMediaStatusByID($productId: ID!) {
      product(id: $productId) {
        media(first: 100) {
          nodes {
            id
            alt
            mediaContentType
            status
            mediaErrors {
              code
              details
              message
            }
            mediaWarnings {
              code
              message
            }
          }
        }
      }
    }
    """
    variables = {"productId": product_id}
    response = run_query(query, variables)
    json_data = response.json()
    return json_data['data']['product']['media']['nodes']


def wait_for_media_processing_completion(product_id, timeout_minutes=10):
    poll_interval = 5  # Poll every 5 seconds
    max_attempts = int((timeout_minutes * 60) / poll_interval)
    attempts = 0

    while attempts < max_attempts:
        media_nodes = product_media_status(product_id)
        processing_items = [
            node for node in media_nodes if node['status'] == "PROCESSING"]
        failed_items = [
            node for node in media_nodes if node['status'] == "FAILED"]

        if failed_items:
            logger.info("Some media failed to process:")
            for item in failed_items:
                logger.info(f"Status: {item['status']}, Errors: {
                            item['mediaErrors']}")
            return False

        if not processing_items:
            logger.info("All media have completed processing.")
            return True

        logger.info("Media still processing. Waiting...")
        time.sleep(poll_interval)
        attempts += 1

    logger.info("Timeout reached while waiting for media processing completion.")
    return False


def upload_and_assign_images_to_product(product_id, drive_image_details):
    logger.info(
        f'number of images being downloaded/uploaded: {len(drive_image_details)}')
    staged_targets = generate_staged_upload_targets(drive_image_details)
    logger.info(f'generated staged upload targets: {len(staged_targets)}')
    upload_images_to_shopify(staged_targets, drive_image_details)
    logger.info(f"Images uploaded for {
                product_id}, going to remove existing and assign.")
    remove_product_media_by_product_id(product_id)
    assign_images_to_product([target['resourceUrl'] for target in staged_targets],
                             alts=[f['name'] for f in drive_image_details],
                             product_id=product_id)


def variant_id_for_sku(sku):
    query = """
    {
      productVariants(first: 10, query: "sku:'%s'") {
        nodes {
          id
          title
        }
      }
    }
    """ % sku

    response = run_query(query, {})
    json_data = response.json()

    if len(json_data['data']['productVariants']['nodes']) != 1:
        raise Exception(f"Multiple variants found for {sku}: {
                        json_data['data']['productVariants']['nodes']}")

    return json_data['data']['productVariants']['nodes'][0]['id']


def variant_by_variant_id(variant_id):
    query = """
    {
      productVariant(id: "%s") {
        id
        title
        media(first: 5) {
          nodes {
            id
          }
        }
      }
    }
    """ % variant_id

    response = run_query(query, {})
    json_response = response.json()

    return json_response['data']['productVariant']


def detach_variant_media(product_id, variant_id, media_id):
    query = """
    mutation productVariantDetachMedia($productId: ID!, $variantMedia: [ProductVariantDetachMediaInput!]!) {
      productVariantDetachMedia(productId: $productId, variantMedia: $variantMedia) {
        product {
          id
        }
        productVariants {
          id
          media(first: 5) {
            nodes {
              id
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    variables = {
        "productId": product_id,
        "variantMedia": [{
            "variantId": variant_id,
            "mediaIds": [media_id]
        }]
    }
    return run_query(query, variables)


def assign_image_to_skus(product_id, image_position, skus):
    logger.info(f'assigning a variant image to {skus}')
    variant_ids = [variant_id_for_sku(sku) for sku in skus]

    variants = [variant_by_variant_id(variant_id)
                for variant_id in variant_ids]
    for variant in variants:
        if len(variant['media']['nodes']) > 0:
            detach_variant_media(product_id,
                                 variant['id'],
                                 variant['media']['nodes'][0]['id'])

    media_nodes = product_media_status(product_id)
    media_id = media_nodes[image_position]['id']

    query = """
    mutation productVariantAppendMedia($productId: ID!, $variantMedia: [ProductVariantAppendMediaInput!]!) {
      productVariantAppendMedia(productId: $productId, variantMedia: $variantMedia) {
        product {
          id
        }
        productVariants {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    variables = {
        "productId": product_id,
        "variantMedia": [{"variantId": vid, "mediaIds": [media_id]} for vid in variant_ids]
    }

    return run_query(query, variables)


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
    product_id = product_id_by_title(product_title)

    drive_image_details = []
    variant_image_positions = []

    for drive_id, skus in zip(drive_ids, skuss):
        variant_image_positions.append(len(drive_image_details))
        drive_image_details += get_drive_image_details(
            drive_id, skus[0], image_prefix)

    logger.debug(f"Drive Image Details: {drive_image_details}")

    upload_and_assign_images_to_product(product_id, drive_image_details)

    for skus, image_position in zip(skuss, variant_image_positions):
        assign_image_to_skus(product_id, image_position, skus)


def get_sheet_index_by_title(sheet_id, sheet_title):
    worksheet = gspread_access().open_by_key(sheet_id)
    for meta in worksheet.fetch_sheet_metadata()['sheets']:
        if meta['properties']['title'] == sheet_title:
            return meta['properties']['index']
    raise RuntimeError(f'Did not find a sheet named {sheet_title}')


def products_info_from_sheet(shop_name, sheet_id, sheet_index=0):
    worksheet = gspread_access().open_by_key(sheet_id).get_worksheet(sheet_index)
    rows = worksheet.get_all_values()

    if shop_name == 'kumej':
        title_column_index = 2
        color_column_index = 3
        sku_column_index = 5
        link_column_index = 13
        start_row = 4
    elif shop_name == 'gbhjapan':
        title_column_index = 5
        color_column_index = 6
        sku_column_index = 8
        link_column_index = 14
        start_row = 4
    else:
        raise RuntimeError(f'unknown shop {shop_name}')

    products = []
    current_product_title = ''

    for row in rows[start_row - 1:]:  # Skip headers
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
        sku = row[sku_column_index].strip()
        assert sku
        if color != current_color:
            products[-1]['skuss'].append([sku])
        else:
            products[-1]['skuss'][-1].append(sku)
        link = row[link_column_index].strip()
        if link:
            if not link.startswith('http'):
                logger.exception(f'\n!!! malformed URL: {link} !!!\n')
            products[-1]['links'].append(link)
    return products


def main():
    image_prefix = UPLOAD_IMAGE_PREFIX
    sheet_index = get_sheet_index_by_title(GSPREAD_ID, SHEET_TITLE)
    logger.info(f'sheet index of {SHEET_TITLE} is {sheet_index}')
    product_details = products_info_from_sheet(
        shop_name=SHOPNAME, sheet_id=GSPREAD_ID, sheet_index=sheet_index)
    for pr in product_details:
        drive_ids = [pp.rsplit('/', 1)[-1].replace('?usp=drive_link', '').replace('?usp=sharing', '')
                     for pp in pr['links']]
        logger.info(f'''
              processing {pr['product_title']}
              SKUs: {pr['skuss']}
              Folders: {drive_ids}
              ''')
        process_product_images_to_shopify(
            image_prefix, pr['product_title'], drive_ids, pr['skuss'])

    # product_title = 'Twisted Neck Superfine Merino Wool Cardigan';
    # drive_ids = [
    #           '1qEME0URUWETd_fepr3KJFSz2EhXCxjoJ',
    #           '1ACt4g7tqigsmXYemUCc9KnDynW20E5Iz',
    #           '15VwlvmnC7EBmOZaslyMq40KyHXcWt63g'
    #       ];
    # skuss = [
    #     ['KM-24FW-SW01-IV-S',
    #       'KM-24FW-SW01-IV-M'],
    #     ['KM-24FW-SW01-MT-S',
    #       'KM-24FW-SW01-MT-M'],
    #     ['KM-24FW-SW01-DBR-S',
    #       'KM-24FW-SW01-DBR-M']
    #   ];


if __name__ == "__main__":
    main()
