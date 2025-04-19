import csv
import os

csv_path = '/Users/taro/Downloads/products_export_1 (1).csv'
images_dir = '/Users/taro/Downloads/EC_listcut'


def rename_files():
    original_image_names = os.listdir(images_dir)
    image_names = list(map(str.lower, original_image_names))
    out_lines = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for l in reader:
            title = l['Title'] or title
            color = l['Option1 Value']

            if color:
                sku = l['Variant SKU']
                name_key = f'{title.lower()} {color.lower()}.jpg'
                if not name_key in image_names:
                    print(f'missing: {name_key}')
                    continue
                file_name = original_image_names[image_names.index(name_key)]
                os.rename(f'{images_dir}/{file_name}',
                          f'{images_dir}/{sku}_0_product_cover.jpg')


rename_files()
