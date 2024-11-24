import pandas as pd

products = pd.read_csv('/Users/taro/Downloads/kume_products_export_20241124.csv')
products = products[products['Variant SKU'].notnull()]
products['Variant SKU'] = products['Variant SKU'].apply(lambda x: x[1:] if x.startswith("'") else x)
products = products.ffill()
products = products[products['Status'] == 'active']
products = products[['Handle', 'Title', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU', 'Tags']]
skus = products['Variant SKU'].to_list()

df = pd.read_csv('/Users/taro/Downloads/(KR) KUME Japan EC BLACK FRIDAY LIST - BLACK FRIDAY.csv', header=1)
df = df[1:]
df = df[['品番\n품번', '商品名\n상품명', 'カラー\n컬러', 'サイズ\n사이즈', 'BLACK FRIDAY\n할인율', '本国確保在庫数\n확보가능 재고수']]
df.rename(columns=lambda c: c.replace('\n', ' '), inplace=True)
df = df[df['BLACK FRIDAY 할인율'].notnull()]
df.loc[df['品番 품번'].eq('KM-24FW-SW04-WYL-S'), '品番 품번'] = 'KM-24FW-SW04-WYE-S'
df.loc[df['品番 품번'].eq('KM-24FW-SW04-WYL-M'), '品番 품번'] = 'KM-24FW-SW04-WYE-M'
df.loc[df['品番 품번'].eq('KM-24FW-BL04-IV-S'), '品番 품번'] = 'KM-24FW-BL04-IV-F'
df.loc[df['品番 품번'].eq('KM-24FW-BL04-IV-M'), '品番 품번'] = 'KM-24FW-BL04-IV-F'
products = products[products['Variant SKU'].isin(df['品番 품번'].to_list())]

for percentage in dict.fromkeys(df['BLACK FRIDAY 할인율'].to_list()):
    new_tag = f'2024 BF {percentage} OFF'
    skus = df[df['BLACK FRIDAY 할인율'] == percentage]['品番 품번'].to_list()
    cond = products['Variant SKU'].isin(skus)
    print(new_tag, len(set(skus)), len(products[cond]))
    products.loc[cond, 'Tags'] = products.loc[cond, 'Tags'].apply(lambda tags: ', '.join([tags, new_tag]))

s = products.groupby('Handle')['Tags'].nunique()
assert s[s > 1].empty, f'multiple tags for a handle:\n{s[s > 1]}'

products = products[['Handle', 'Title', 'Tags']].drop_duplicates()
products.to_csv('/Users/taro/Downloads/kume_bf_tags.csv', index=False)
