import utils
client = utils.client('what-youth-japan')
import pandas as pd
df = pd.read_csv(r'/Users/taro/Documents/PMA\ Inc/leisure\ allstars/20240325_price_update_OF240225-EPOKHE-2024年3月よりの新上代記載\ /EPOKHEオーダーシート-Table\ 1.csv'.replace('\\', ''), header=10)

def get_price(price):
    try:
        return int(price.replace('¥', '').replace(',', ''))
    except Exception:
        pass

skus_not_found = []
unmatch = []
match = []

for sku, price in zip(df['スタイルナンバー'], df['上代（税込）.1']):
    price = get_price(price)
    if price:
        variant = client.variant_by_sku(sku)
        if not variant:
            skus_not_found.append(sku)
        else:
            s_price = int(variant[0]['price'])
            if price != s_price:
                unmatch.append((sku, price, s_price))
            else:
                match.append((sku, price))


print('skus_not_found:')
for sku in skus_not_found:
    print(sku)

print()
print('match:')
for sku, price in match:
    print(f'{sku}\t{price}')

print()
print('unmatch:')
for sku, price, s_price in unmatch:
    print(f'{sku}\t{price}\t{s_price}')

df = pd.DataFrame.from_records(unmatch)
df.to_csv(r'/Users/taro/Documents/PMA Inc/leisure allstars/20250508_price_unmatch.csv', index=False)
