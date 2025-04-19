import os
import utils

SHEET_TITLE = 'Products Master'
localdir = '/Users/taro/Downloads/apricot_studios_model_info_images'

def main():
    client = utils.client('apricot-studios')
    model_info_images = [client.sanitize_image_name(p) for p in os.listdir(localdir)]
    rows = client.worksheet_rows(client.sheet_id, SHEET_TITLE)

    for row in rows[1:]:
        title = row[1].strip()
        if not title:
            continue
        print(f'processing {title}')
        product_id = client.product_id_by_title(title)
        descriptionHtml = client.product_description_by_product_id(product_id)
        for name in model_info_images:
            if name in descriptionHtml:
                descriptionHtml = descriptionHtml.replace(name, 'model_info.png')
                print('going to update description of {title}')
                client.update_product_description(product_id, descriptionHtml)
                break


if __name__ == '__main__':
    main()
