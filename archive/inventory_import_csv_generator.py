import pandas as pd
stocks = pd.read_csv('/Users/taro/Downloads/inventory_export_1-3.csv')

products = pd.read_csv(
    '/Users/taro/Downloads/(KR) KUME Japan EC Product Details - GS 20240828 - Product Import CSV (6).csv')

handles = pd.read_csv('/Users/taro/Downloads/products_export_1-9.csv')
handles = handles[handles['Title'].notnull()][['Handle', 'Title']]
title_handle_map = {row['Title']: row['Handle'] for _, row in handles.iterrows()}

rows = []
for index, row in products.iterrows():
    title = row['Title'].strip()
    option1 = row['Option1 Value'].strip()
    option2 = row['Option2 Value'].strip()
    rows.append([title_handle_map[title], title,
                 row['Option1 Name'], option1, row['Option2 Name'], option2, '', '', row['Variant SKU'],
                 'Envycube Warehouse', 0, 0, 0, 0, 0])
    rows.append([title_handle_map[title], title,
                 row['Option1 Name'], option1, row['Option2 Name'], option2, '', '', row['Variant SKU'],
                 'KUME Warehouse', 0, 0, 0, row['Variant Inventory Qty'], row['Variant Inventory Qty']])

columns = ['Handle', 'Title', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'SKU',
           'Location', 'Incoming', 'Unavailable', 'Committed', 'Available', 'On hand']
inventory = pd.DataFrame(rows, columns=columns)


inventory.to_csv('/Users/taro/Downloads/inventory_import_20240909.csv', index=False)
