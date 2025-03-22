import logging
import os
import string
from dotenv import load_dotenv
from google_utils import get_sheet_index_by_title, gspread_access
from shopify_utils import (run_query, product_id_by_title, medias_by_product_id,
                           generate_staged_upload_targets, upload_images_to_shopify,remove_product_media_by_product_id, assign_images_to_product,
                           assign_image_to_skus, upload_and_assign_description_images_to_shopify)

load_dotenv(override=True)
SHOPNAME = 'apricot-studios'
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
print(ACCESS_TOKEN)
GOOGLE_CREDENTIAL_PATH = os.getenv('GOOGLE_CREDENTIAL_PATH')

UPLOAD_IMAGE_PREFIX = 'upload_20250304'
IMAGES_LOCAL_DIR = '/Users/taro/Downloads/apricotstudios_20250304/'
GSPREAD_ID = '1yVzpgcrgNR7WxUYfotEnhYFMbc79l1O4rl9CamB2Kqo'
SHEET_TITLE = 'Products Master'
DUMMY_PRODUCT = 'gid://shopify/Product/9032277197056'

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)




def upload_and_assign_images_to_product(product_id, local_paths):
    mime_types = [f'image/{local_path.rsplit('.', 1)[-1].lower()}' for local_path in local_paths]
    staged_targets = generate_staged_upload_targets(SHOPNAME, ACCESS_TOKEN, local_paths, mime_types)
    logger.info(f'generated staged upload targets: {len(staged_targets)}')
    upload_images_to_shopify(staged_targets, local_paths, mime_types)
    logger.info(f"Images uploaded for {product_id}, going to remove existing and assign.")
    remove_product_media_by_product_id(SHOPNAME, ACCESS_TOKEN, product_id)
    assign_images_to_product(SHOPNAME, ACCESS_TOKEN,
                             [target['resourceUrl'] for target in staged_targets],
                             alts=[local_path.rsplit('/', 1)[-1] for local_path in local_paths],
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


def products_info_from_sheet(sheet_id, sheet_index=0):
    worksheet = gspread_access(GOOGLE_CREDENTIAL_PATH).open_by_key(sheet_id).get_worksheet(sheet_index)
    rows = worksheet.get_all_values()

    # start_row 1 base, columns are 0 base
    title_column_index = 1
    product_main_images_index = 14
    product_detail_images_index = 15
    color_column_index = 16
    variant_images_index = 17
    sku_column_index = 19
    start_row = 2

    products = []
    current_product_title = ''

    for row in rows[start_row - 1:]:  # Skip headers
        sku = row[sku_column_index].strip()
        if not sku:
            break
        product_title = row[title_column_index].strip()
        product_main_images_link = row[product_main_images_index] or product_main_images_link
        product_detail_images_link = row[product_detail_images_index] or product_detail_images_link
        if not product_title:
            product_title = current_product_title
        if product_title != current_product_title:
            products.append(dict(product_title=product_title,
                                 skuss=[],
                                 product_main_images_link=product_main_images_link,
                                 product_detail_images_link=product_detail_images_link,
                                 variant_images_links=[]))
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
        variant_images_link = row[variant_images_index]
        if variant_images_link:
            products[-1]['variant_images_links'].append(variant_images_link)
    return products


def image_prefix(title):
    return title.translate(str.maketrans(string.punctuation, '_' * len(string.punctuation)))

def main():
    from dropbox_utils import download_and_rename_images_from_dropbox
    sheet_index = get_sheet_index_by_title(GOOGLE_CREDENTIAL_PATH, GSPREAD_ID, SHEET_TITLE)
    logger.info(f'sheet index of {SHEET_TITLE} is {sheet_index}')
    product_details = products_info_from_sheet(sheet_id=GSPREAD_ID, sheet_index=sheet_index)

    reprocess_titles, reprocess_skus = [], []
    reprocess_from_sku = ''

    if reprocess_from_sku:
        import itertools
        all_skus = list(itertools.chain(sku for pr in product_details for skus in pr['skuss'] for sku in skus))

    for pr in product_details:
        if ((all((not(reprocess_skus), not(reprocess_titles))) or
            any(sku in skus for sku in reprocess_skus for skus in pr['skuss']) or
            pr['product_title'] in reprocess_titles) and
            (not reprocess_from_sku or reprocess_from_sku and any(all_skus.index(sku) >= all_skus.index(reprocess_from_sku) for skus in pr['skuss'] for sku in skus))):

            image_pathss = [download_and_rename_images_from_dropbox(pr['product_title'],
                                                                    pr['product_main_images_link'],
                                                                    prefix=f'{image_prefix(pr['product_title'])}_product_main')]
            for skus, variant_image_link in zip(pr['skuss'], pr['variant_images_links']):
                image_pathss += [download_and_rename_images_from_dropbox(pr['product_title'], variant_image_link, skus[0])]
            import pprint
            pprint.pprint(image_pathss)
            product_id = product_id_by_title(SHOPNAME, ACCESS_TOKEN, pr['product_title'])
            image_position = len(image_pathss[0])
            upload_and_assign_images_to_product(product_id, sum(image_pathss, []))
            for variant_image_paths, skus in zip(image_pathss[1:], pr['skuss']):
                print(f'assing variant image at position {image_position} to {skus}')
                assign_image_to_skus_by_position(product_id, image_position, skus)
                image_position += len(variant_image_paths)

            detail_image_paths = download_and_rename_images_from_dropbox(pr['product_title'],
                                                                         pr['product_detail_images_link'],
                                                                         prefix=f'{image_prefix(pr['product_title'])}_product_detail')
            upload_and_assign_description_images_to_shopify(SHOPNAME, ACCESS_TOKEN, product_id, detail_image_paths, DUMMY_PRODUCT, 'https://cdn.shopify.com/s/files/1/0745/9435/3408')

if __name__ == "__main__":
    main()
