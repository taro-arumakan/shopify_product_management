
import string
import google_api_interface
import shopify_graphql_client
import utils

IMAGES_LOCAL_DIR = '/Users/taro/Downloads/rawrowr20250321/'
DUMMY_PRODUCT = 'gid://shopify/Product/8773753700593'
SHOPIFY_FILE_URL_PREFIX = 'https://cdn.shopify.com/s/files/1/0726/9187/6081/'

additional_punctuation_chars = '‘’“” '
punctuation_chrs = string.punctuation + additional_punctuation_chars
punctuation_translator = str.maketrans(punctuation_chrs, '_' * len(punctuation_chrs))

def main():
    cred = utils.credentials('rawrowr')
    gai = google_api_interface.get(cred.shop_name)
    folders = gai.list_folders(parent_folder_id='1ijec5ijfvFLvpzZGW7KmM7D0tQkUDky7')
    sgc = shopify_graphql_client.get(cred.shop_name)
    restart_from = "R TRUNK FRAME ep.3 88L _ 29'' 933"
    for index, f in enumerate(folders):
        if f['name'] == restart_from:
            break
    for f in folders[index:]:
        dir_id = f['id']
        name = f['name']
        if name != "R TRUNK FRAME ep.3 84L _ 20’’":
            prefix = name.translate(punctuation_translator)
            local_paths = gai.drive_images_to_local(dir_id, IMAGES_LOCAL_DIR, download_filename_prefix=f'{prefix}_')
            if local_paths:
                product_id = sgc.product_id_by_title(name.replace('_', '/'))
                print(f'upload {len(local_paths)} images to {product_id}')
                sgc.upload_and_assign_description_images_to_shopify(product_id, local_paths, DUMMY_PRODUCT,
                                                                    SHOPIFY_FILE_URL_PREFIX)

if __name__ == '__main__':
    main()
