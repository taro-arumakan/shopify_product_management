import os
import pprint
import shopify_graphql_client

DUMMY_PRODUCT = 'gid://shopify/Product/9035094130944'

localdir = '/Users/taro/Downloads/apricot_studios_psd_to_jpg'
other_localdir = '/Users/taro/Downloads/apricot_studios'

def names_to_ignore(local_new_path):
    parts = local_new_path.rsplit('/', 1)[-1].split('_')
    seq = str(int(parts[-2]) - 1).zfill(2)
    return ['_'.join(parts[:-2] + [seq] + parts[-1:])] + [local_new_path]

def main():
    paths_by_product_title = {}
    for path in os.listdir(localdir):
        if '_product_main' in path:
            print(f'ignoring translated file: {path}')
        else:
            paths_by_product_title.setdefault(path.split('_')[0], []).append(f'{localdir}/{path}')

    for product_title, paths in paths_by_product_title.items():
        print(product_title)
        ignore_names = sum([names_to_ignore(path) for path in paths], [])
        other_paths = [f'{other_localdir}/{product_title}/{p}' for p in os.listdir(f'{other_localdir}/{product_title}')
                        if '_product_detail_' in p and
                            not p.endswith('.psd') and
                            not p in ignore_names]
        all_paths = sorted(paths + other_paths, key=lambda x: int(x.rsplit('/', 1)[-1].split('_')[-1].split('.')[0]))
        sgc = shopify_graphql_client.get('apricot-studidos')
        product_id = sgc.product_id_by_title(product_title)
        print(product_id)
        pprint.pprint(all_paths, width=150)
        sgc.upload_and_assign_description_images_to_shopify(product_id, all_paths, DUMMY_PRODUCT, 'https://cdn.shopify.com/s/files/1/0745/9435/3408')
