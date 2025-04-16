import os
import pprint
from dotenv import load_dotenv
import google_api_interface
import shopify_graphql_client

from utils import credentials

load_dotenv(override=True)

SHEET_TITLE = 'Products Master'

localdir = '/Users/taro/Downloads/apricot_studios_model_info_images'

def main():
    cred = credentials('apricot-studios')
    sgc = shopify_graphql_client.get(cred.shop_name)
    model_info_images = [sgc.sanitize_image_name(p) for p in os.listdir(localdir)]
    gai = google_api_interface.get(cred.shop_name)
    rows = gai.worksheet_rows(gai.sheet_id, SHEET_TITLE)

    for row in rows[1:]:
        title = row[1].strip()
        if not title:
            continue
        print(f'processing {title}')
        product_id = sgc.product_id_by_title(title)
        descriptionHtml = sgc.product_description_by_product_id(product_id)
        for name in model_info_images:
            if name in descriptionHtml:
                descriptionHtml = descriptionHtml.replace(name, 'model_info.png')
                print('going to update description of {title}')
                sgc.update_product_description(product_id, descriptionHtml)
                break


if __name__ == '__main__':
    main()
