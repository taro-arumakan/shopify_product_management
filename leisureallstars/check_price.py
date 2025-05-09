import utils

client = utils.client("what-youth-japan")
import pandas as pd

df = pd.read_csv(
    r"/Users/taro/Documents/PMA Inc/leisure allstars/SOH250508-EPOKHE-4.csv", header=10
)


def get_price(price):
    try:
        return int(price.replace("¥", "").replace(",", ""))
    except Exception:
        pass


skus_not_found = []
unmatch = []
match = []
multiple_sksu = []

for sku, price in zip(df["スタイルナンバー"], df["上代（税込）"]):
    price = get_price(price)
    if price:
        try:
            variant = client.variant_by_sku(sku)
        except utils.MultipleVariantsFoundException as ex:
            print(ex)
            multiple_sksu.append((sku, price))
        except utils.NoVariantsFoundException:
            skus_not_found.append(sku)
        else:
            s_price = int(variant["price"])
            if price != s_price:
                unmatch.append((sku, price, s_price))
            else:
                match.append((sku, price))


print("skus_not_found:")
for sku in skus_not_found:
    print(sku)

print()
print("match:")
for sku, price in match:
    print(f"{sku}\t{price}")

print()
print("unmatch:")
for sku, price, s_price in unmatch:
    print(f"{sku}\t{price}\t{s_price}")

print()
print("multiple for a sku:")
for sku, price in multiple_sksu:
    print(f"{sku}\t{price}")

df = pd.DataFrame.from_records(unmatch)
df.to_csv(
    r"/Users/taro/Documents/PMA Inc/leisure allstars/20250508_price_unmatch_2.csv",
    index=False,
)
