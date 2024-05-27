import pandas as pd
import re

csv_path = '/Users/taro/Downloads/products_export_1 (1).csv'
image_url_base = 'https://cdn.shopify.com/s/files/1/0692/1981/1587/files'
url_pattern = re.compile(r'(https\://.*?_\d+)_?.*?\.jpg.*')

out_products_csv_path = '/Users/taro/Downloads/products_import.csv'
out_variants_csv_path = '/Users/taro/Downloads/variants_import.csv'


def update_sku_image(sku, df):
    for i in (0, 1):
        # cover image right now is named either with _0.jpg or _1.jpg, so check both.
        s = df[df['Image Src'].str.contains(f'{sku}_{i}')]
        if not s.empty:
            df.loc[df['Image Src'].str.contains(
                f'{sku}_{i}'), 'Image Src'] = sku_image_url(sku)
            return df
    raise RuntimeError(f'image path not found for {sku}')


def update_variant_image(sku, df):
    df.loc[df['Variant SKU'] == sku, 'Variant Image'] = f'{
        image_url_base}/{sku}_0_product_cover.jpg'
    return df


def format_url(url):
    match = url_pattern.match(url)
    if match:
        return f'{match[1]}.jpg'
    return url


def sku_image_url(sku):
    return f'{image_url_base}/{sku}_0_product_cover.jpg'


def generate():
    df = pd.read_csv(csv_path)

    df['Image Src'] = df['Image Src'].apply(format_url)

    df.loc[df['Variant SKU'].notnull(), 'Variant Image'] = df[df['Variant SKU'].notnull()].apply(
        lambda x: sku_image_url(x['Variant SKU']), axis=1)

    for i, row in df[df['Variant SKU'].notnull()].iterrows():
        df = update_sku_image(row['Variant SKU'], df)

    # product update csv
    df[['Handle', 'Title', 'Image Src', 'Image Position']].to_csv(
        out_products_csv_path, index=False)

    # variant update csv - variant related columns only
    df[df['Variant SKU'].notnull()][['Handle', 'Title', 'Option1 Name', 'Option1 Value',
                                    'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value',
                                     'Variant SKU', 'Variant Image']].to_csv(out_variants_csv_path, index=False)


generate()
