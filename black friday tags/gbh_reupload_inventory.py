import pandas as pd

products = pd.read_csv('/Users/taro/Downloads/gbh_products_export_20241120.csv')
products = products[products['Variant SKU'].notnull()]
products['Variant SKU'] = products['Variant SKU'].apply(lambda x: x[1:] if x.startswith("'") else x)
products = products.ffill()
products = products[products['Status'] == 'active']
products = products[['Handle', 'Title', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU', 'Variant Image']]

df = pd.read_csv(r'/Users/taro/Downloads/GBH\ Japan\ EC_2024\ Black\ Friday\ -\ JP\ RRP\ \(판가\)\ COSME.csv'.replace('\\', ''), header=1)
df = df[['CODE', 'ITEM', 'COLOR', 'BF 割引率']]
df = df[(df['BF 割引率'].notnull()) & (df['BF 割引率']!='X')]

skus = df['CODE'].to_list()

df = pd.read_csv(r'/Users/taro/Downloads/GBH\ Japan\ EC_2024\ Black\ Friday\ -\ JP\ RRP\ \(판가\)\ HOME.csv'.replace('\\', ''), header=1)
df = df[['CODE', 'ITEM', 'COLOR', 'BF 割引率']]
df = df[(df['BF 割引率'].notnull()) & (df['BF 割引率']!='X')]

cond = (~df['CODE'].isin(skus)) & (df['CODE'].apply(lambda x: len(x)) == 4)
df.loc[cond, 'CODE'] = df.loc[cond, 'CODE'].apply(lambda x: '0' + x)

skus += df['CODE'].to_list()

products[products['Variant SKU'].isin(skus)]
