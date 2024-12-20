import pandas as pd
df = pd.read_csv('/Users/taro/Downloads/inventory_export_1.csv')
new_inventory = pd.read_csv('/Users/taro/Downloads/(KR) KUME Japan EC OUTER FAIR - OUTER FAIR.csv', header=[1])
new_inventory = new_inventory[1:]
skus = new_inventory['品番\n품번'].to_list()
assert not [sku for sku in skus if sku not in df['SKU'].to_list()], 'missing SKU'

df = df[['Handle', 'Title', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'SKU', 'Location', 'Available', 'On hand']]
df = df[df['SKU'].isin(skus)]
# df.groupby(['Handle', 'Title', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'SKU']).sum()
for i, row in new_inventory.iterrows():
    df.loc[(df['SKU'] == row['品番\n품번']) & (df['Location']=='KUME Warehouse'), 'Available'] = row['本国確保在庫数\n확보가능 재고수']
    df.loc[(df['SKU'] == row['品番\n품번']) & (df['Location']=='KUME Warehouse'), 'On hand'] = row['本国確保在庫数\n확보가능 재고수']
    df.loc[(df['SKU'] == row['品番\n품번']) & (df['Location']=='Envycube Warehouse'), 'Available'] = 0
    df.loc[(df['SKU'] == row['品番\n품번']) & (df['Location']=='Envycube Warehouse'), 'On hand'] = 0


df.to_csv('/Users/taro/Downloads/20241118_update_inventory.csv', index=False)
