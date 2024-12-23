from functools import partial
import pandas as pd

products = pd.read_csv('/Users/taro/Downloads/archive-epke-products_export_1.csv')
products = products[products['Variant SKU'].notnull()]
products['Variant SKU'] = products['Variant SKU'].apply(lambda x: x[1:] if x.startswith("'") else x)
products = products.ffill()
# products = products[products['Status'] == 'active']
products = products[['Handle', 'Title', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU', 'Tags']]
skus = products['Variant SKU'].to_list()

df = pd.read_csv(r'/Users/taro/Downloads/Archivepke 24SS LINE SHEET.xlsx - 20251_1 SALE LIST.csv', header=3)
df = df[['SKU', 'Products①', 'Products②', 'Color', 'Size', 'Off Rate']]
df = df[(df['Off Rate'].notnull()) & (df['Off Rate'].str.endswith('%'))].reset_index(drop=True)
df['SKU'] = df['SKU'].str.strip()

# cond = (~df['品番'].isin(skus)) & (df['品番'].apply(lambda x: len(x)) == 4)
# df.loc[cond, '品番'] = df.loc[cond, '品番'].apply(lambda x: '0' + x)

print(f'missing SKU:\n{df[~df['SKU'].isin(skus)]}')

products = products[products['Variant SKU'].isin(df['SKU'].to_list())]

def update_tags(tags, new_tag):
    tags = tags.split(', ')
    tags = [tag for tag in tags if not tag.startswith('2024 Black Friday ')]
    return ', '.join(tags + [new_tag])

for percentage in dict.fromkeys(df['Off Rate'].to_list()):
    new_tag = f'2025 New Year {percentage} OFF'
    target_skus = df[df['Off Rate']==percentage]['SKU'].to_list()
    cond = products['Variant SKU'].isin(target_skus)
    print(new_tag, len(target_skus), len(products[cond]))
    f = partial(update_tags, new_tag=new_tag)
    products.loc[cond, 'Tags'] = products.loc[cond, 'Tags'].apply(f)

s = products.groupby('Handle')['Tags'].nunique()
assert s[s > 1].empty, f'multiple tags for a handle:\n{s[s > 1]}'

products.to_csv('/Users/taro/Downloads/archive-epke_2025_holiday_new_tags.csv', index=False)
