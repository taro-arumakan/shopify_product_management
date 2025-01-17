import pandas as pd
import numpy as np

def generate_new_price_df(category):
    df = pd.read_csv(f'/Users/taro/Downloads/GBH Japan EC Product Details - JP RRP (판가) {category.upper()}変更_0110.csv', header=1)
    new_price = df[['CODE', 'JP RRP\nTax in']]
    products = pd.read_csv('/Users/taro/Downloads/products_export_1-5.csv')
    products = products[['Handle', 'Title', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value',
                         'Variant SKU', 'Variant Price', 'Variant Compare At Price', 'Tags']]
    products = products[products['Variant SKU'].notnull()]
    for col in ['Handle', 'Title', 'Tags']:
        products[col] = products[col].ffill()
    for option_name, option_value in [("Option1 Name", "Option1 Value"),
                                      ("Option2 Name", "Option2 Value"),
                                      ("Option3 Name", "Option3 Value")]:
        products[option_name] = products[option_name].where(products[option_value].isnull(), products[option_name].ffill())

    products = products[products['Tags'].str.contains(category.upper())]
    products['Variant SKU'] = products['Variant SKU'].apply(lambda x: x[1:] if x.startswith("'") else x)

    def lookup_price(sku):
        new_price_df = new_price[new_price['CODE']==sku]
        assert len(new_price_df) <= 1
        if len(new_price_df) == 1:
            return new_price[new_price['CODE']==sku].iloc[0]['JP RRP\nTax in'].replace('¥', '').replace(',', '').strip()
        else:
            return products[products['Variant SKU'] == sku].iloc[0]['Variant Price']

    products['New Variant Price'] = products['Variant SKU'].apply(lookup_price)
    products['New Compare At Price'] = products['Variant SKU'].apply(lookup_price)
    products = products[['Handle', 'Title', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU',
                         'New Variant Price', 'New Compare At Price', 'Variant Price', 'Variant Compare At Price']]
    p = 'Variant Price'
    cp = 'Variant Compare At Price'
    products['Price Diff'] = products.apply(lambda x: int(x[p] if np.isnan(x[cp]) else x[cp]) - int(x[f'New {p}']), axis=1)

    products.rename(columns={'New Variant Price': 'Variant Price', 'New Compare At Price': 'Variant Compare At Price',
                             'Variant Price': 'Old Variant Price', 'Variant Compare At Price': 'Old Compare At Price'},
                     inplace=True)
    return products

dfs = [generate_new_price_df(c) for c in ['APPAREL', 'HOME']]
res = pd.concat(dfs)

res = res[['Handle', 'Title', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU',
           'Variant Price', 'Variant Compare At Price']]
res.to_csv('/Users/taro/Downloads/20250110_new_price.csv', index=False)
