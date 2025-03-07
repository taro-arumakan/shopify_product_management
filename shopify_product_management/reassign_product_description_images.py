import os
import pprint
from dotenv import load_dotenv
from shopify_utils import product_id_by_title, upload_and_assign_description_images_to_shopify

load_dotenv(override=True)

SHOPNAME = 'apricot-studios'
DUMMY_PRODUCT = 'gid://shopify/Product/9035094130944'

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
print(ACCESS_TOKEN)
GOOGLE_CREDENTIAL_PATH = os.getenv('GOOGLE_CREDENTIAL_PATH')


localdir = '/Users/taro/Downloads/apricot_studios_psd_to_jpg'
paths_by_product_title = {}
for path in os.listdir(localdir):
    paths_by_product_title.setdefault(path.split('_')[0], []).append(f'{localdir}/{path}')


other_localdir = '/Users/taro/Downloads/apricot_studios'

def sanitize_image_name(image_name):
    return image_name.replace(' ', '_').replace('[', '').replace(']', '_').replace('(', '').replace(')', '')

for product_title, paths in paths_by_product_title.items():
  print(product_title)
  product_id = product_id_by_title(SHOPNAME, ACCESS_TOKEN, product_title)
  print(product_id)
  other_paths = [f'{other_localdir}/{product_title}/{p}' for p in os.listdir(f'{other_localdir}/{product_title}')
                 if '_product_detail_' in p and not p.endswith('.psd')]
  all_paths = sorted(paths + other_paths, key=lambda x: x.rsplit('/', 1)[-1])
  pprint.pprint([sanitize_image_name(p.rsplit('/', 1)[-1]) for p in all_paths])

  upload_and_assign_description_images_to_shopify(SHOPNAME, ACCESS_TOKEN, product_id, all_paths, DUMMY_PRODUCT)
