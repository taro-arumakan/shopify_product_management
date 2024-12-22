from functools import partial
import pandas as pd

products = pd.read_csv('/Users/taro/Downloads/20241220_gbh_products.csv')
products = products[products['Variant SKU'].notnull()]
products['Variant SKU'] = products['Variant SKU'].apply(lambda x: x[1:] if x.startswith("'") else x)
products = products.ffill()
products = products[products['Status'] == 'active']
products = products[['Handle', 'Title', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU', 'Tags']]
skus = products['Variant SKU'].to_list()

df = pd.read_csv(r'/Users/taro/Downloads/20241218_gbh_holiday_sales_list_COSME.csv', header=1)
df = df[['品番', 'ITEM', 'COLOR', '年末年始\n割引率']]
df = df[(df['年末年始\n割引率'].notnull()) & (df['年末年始\n割引率'].str.endswith('%'))].reset_index()
df['品番'] = df['品番'].str.strip()

# cond = (~df['品番'].isin(skus)) & (df['品番'].apply(lambda x: len(x)) == 4)
# df.loc[cond, '品番'] = df.loc[cond, '品番'].apply(lambda x: '0' + x)

print(f'missing SKU:\n{df[~df['品番'].isin(skus)]}')

products = products[products['Variant SKU'].isin(df['品番'].to_list())]

def update_tags(tags, new_tag):
    tags = tags.split(', ')
    tags = [tag for tag in tags if not tag.startswith('2024 BF ')]
    return ', '.join(tags + [new_tag])

for percentage in dict.fromkeys(df['年末年始\n割引率'].to_list()):
    new_tag = f'2024 Holiday {percentage} OFF COSMETICS'
    skus = df[df['年末年始\n割引率'] == percentage]['品番'].to_list()
    cond = products['Variant SKU'].isin(skus)
    print(new_tag, len(skus), len(products[cond]))
    f = partial(update_tags, new_tag=new_tag)
    products.loc[cond, 'Tags'] = products.loc[cond, 'Tags'].apply(f)

s = products.groupby('Handle')['Tags'].nunique()
assert s[s > 1].empty, f'multiple tags for a handle:\n{s[s > 1]}'

products.to_csv('/Users/taro/Downloads/gbh_2024holiday_new_tags_cosme.csv', index=False)
