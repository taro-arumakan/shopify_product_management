import os
import pprint
from dotenv import load_dotenv
from shopify_utils import product_id_by_title, product_description_by_product_id, update_product_description, sanitize_image_name
from google_utils import get_sheet_index_by_title, gspread_access

load_dotenv(override=True)

SHOPNAME = 'apricot-studios'

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
print(ACCESS_TOKEN)
GOOGLE_CREDENTIAL_PATH = os.getenv('GOOGLE_CREDENTIAL_PATH')
GSPREAD_ID = '1yVzpgcrgNR7WxUYfotEnhYFMbc79l1O4rl9CamB2Kqo'
SHEET_TITLE = 'Products Master'


localdir = '/Users/taro/Downloads/apricot_studios_model_info_images'

def main():
    model_info_images = [sanitize_image_name(p) for p in os.listdir(localdir)]
    sheet_index = get_sheet_index_by_title(GOOGLE_CREDENTIAL_PATH, GSPREAD_ID, SHEET_TITLE)
    worksheet = gspread_access(GOOGLE_CREDENTIAL_PATH).open_by_key(GSPREAD_ID).get_worksheet(sheet_index)
    rows = worksheet.get_all_values()

    for row in rows[1:]:
        title = row[1].strip()
        if not title:
            continue
        print(f'processing {title}')
        product_id = product_id_by_title(SHOPNAME, ACCESS_TOKEN, title)
        descriptionHtml = product_description_by_product_id(SHOPNAME, ACCESS_TOKEN, product_id)
        for name in model_info_images:
            if name in descriptionHtml:
                descriptionHtml = descriptionHtml.replace(name, 'model_info.png')
                print('going to update description of {title}')
                update_product_description(SHOPNAME, ACCESS_TOKEN, product_id, descriptionHtml)
                break


if __name__ == '__main__':
    main()
