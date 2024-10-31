import pandas as pd
df = pd.read_csv('/Users/taro/Downloads/GBH Japan EC Product Details - JP RRP (판가) APPARELのみ変更.csv', header=1)
new_price = df[['CODE', 'JP RRP \nTax in']]
products = pd.read_csv('/Users/taro/Downloads/products_export_1-4.csv')
products = products[products['Option1 Value'].notnull()]
products = products[['Handle', 'Title', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Variant SKU', 'Variant Price', 'Tags']]
products = products.ffill()
products = products[products['Tags'].str.contains('APPAREL')]
products['Variant SKU'] = products['Variant SKU'].apply(lambda x: x[1:] if x.startswith("'") else x)

def lookup_price(sku):
    new_price_df = new_price[new_price['CODE']==sku]
    assert len(new_price_df) <= 1
    if len(new_price_df) == 1:
        return new_price[new_price['CODE']==sku].iloc[0]['JP RRP \nTax in'].replace('¥', '').replace(',', '').strip()
    else:
        return products[products['Variant SKU'] == sku].iloc[0]['Variant Price']

products['New Variant Price'] = products['Variant SKU'].apply(lookup_price)
products = products[['Handle', 'Title', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Variant SKU', 'Variant Price', 'New Variant Price']]
products['Diff'] = products['Variant Price'].apply(int) - products['New Variant Price'].apply(int)
products.to_csv('/Users/taro/Downloads/20241031_new_price_comp.csv')
