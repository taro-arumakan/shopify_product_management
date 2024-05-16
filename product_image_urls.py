import os
import csv

image_dir = '/Users/taro/sc/rohseoul_product_images/images'
url_base = 'https://cdn.shopify.com/s/files/1/0692/1981/1587/files/'


def getImageURLs(sku):
    image_files = sorted(os.listdir(f'{image_dir}/{sku}'), key=lambda x: int(x.split('_')[1].split('.')[0]))
    for name in image_files:
        yield f'https://cdn.shopify.com/s/files/1/0692/1981/1587/files/{name}'


with open(r'product_variant_list.csv') as f:
    reader = csv.DictReader(f)

    with open(r'url_list.csv', 'w') as wf:
        wf.write("Handle,Title,Image Src,Image Position\n")
        title = ''
        i = 0
        for r in reader:
            if r['Title']:
                title = r['Title']
                i = 0
            for url in getImageURLs(r['Variant SKU']):
                i += 1

                wf.write(
                    f"{','.join((r['Handle'], title if i == 1 else '', url, str(i)))}\n")
