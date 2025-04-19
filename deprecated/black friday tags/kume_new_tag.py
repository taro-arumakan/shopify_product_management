from functools import partial
import pandas as pd

products = pd.read_csv('/Users/taro/Downloads/kume_products_export_20241227.csv')
products = products[products['Variant SKU'].notnull()]
products['Variant SKU'] = products['Variant SKU'].apply(lambda x: x[1:] if x.startswith("'") else x)
products = products.ffill()
products = products[products['Status'] == 'active']
products = products[['Handle', 'Title', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU', 'Tags']]
skus = products['Variant SKU'].to_list()

df = pd.read_csv('/Users/taro/Downloads/KUME JP EC FW SEASON OFF LIST.xls - Sheet1.csv', header=1)
df = df[1:]
df = df[['品番\n품번', '商品名\n상품명', 'カラー\n컬러', 'サイズ\n사이즈', 'SEASON OFF\n割引率']]
df.rename(columns=lambda c: c.replace('\n', ' '), inplace=True)
products = products[products['Variant SKU'].isin(df['品番 품번'].to_list())]


def update_tags(tags, new_tag):
    tags = tags.split(', ')
    tags = [tag for tag in tags if not any(tag.startswith(s) for s in ['2024 BF ', '202411 Outerwear Fair '])]
    return ', '.join(tags + [new_tag])


for percentage in dict.fromkeys(df['SEASON OFF 割引率'].to_list()):
    new_tag = f'2025 Holiday Season {percentage} OFF'
    target_skus = df[df['SEASON OFF 割引率'] == percentage]['品番 품번'].to_list()
    cond = products['Variant SKU'].isin(target_skus)
    print(new_tag, len(set(target_skus)), len(products[cond]))
    if len(set(target_skus)) != len(products[cond]):
        print(df[(df['SEASON OFF 割引率']==percentage) & (~df['品番 품번'].isin(skus))])
    f = partial(update_tags, new_tag=new_tag)
    products.loc[cond, 'Tags'] = products.loc[cond, 'Tags'].apply(f)

s = products.groupby('Handle')['Tags'].nunique()
assert s[s > 1].empty, f'multiple tags for a handle:\n{s[s > 1]}'

products = products[['Handle', 'Title', 'Tags']].drop_duplicates()
products.to_csv('/Users/taro/Downloads/kume_holiday_sale_tags.csv', index=False)
