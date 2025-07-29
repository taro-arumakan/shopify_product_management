import logging
import pandas as pd
import utils

logging.basicConfig(level=logging.INFO)

client = utils.client("kumej")

to_be_added_skus = [
    "KM-24SS-OP03-YE-S",
    "KM-24SS-OP03-YE-M",
    "KM-23SP-BL03-IV-S",
    "KM-23SP-BL03-IV-M",
    "KM-23SP-BL03-BK-S",
    "KM-23SP-BL03-BK-M",
    "KM-23SM-SK05-NA-S",
    "KM-23SM-SK05-NA-M",
    "KM-23SM-SK05-NA-L",
    "KM-23SM-PT06-IV-S",
    "KM-23SM-PT06-IV-M",
    "KM-23SM-PT06-IV-L",
    "KM-23SM-PT06-GN-S",
    "KM-23SM-PT06-GN-M",
    "KM-23SM-PT06-GN-L",
    "KM-23SM-OP01-BL-S",
    "KM-23SM-OP01-BL-M",
    "KM-23SM-SK07-MGT-S",
    "KM-23SM-SK07-MGT-M",
]

sku_map = {
    "KM-25SS-SW04-LYE-S": "KM-25SS-SW04-LYL-S",
    "KM-25SS-SW04-LYE-M": "KM-25SS-SW04-LYL-M",
    "KM-25SS-SK05-BC-S": "KM-25SS-SK05-BRK-S",
    "KM-25SS-SK05-BC-M": "KM-25SS-SK05-BRK-M",
    "KM-25HS-PT01-LYE-S": "KM-25HS-PT01-LYL-S",
    "KM-25HS-PT01-LYE-M": "KM-25HS-PT01-LYL-M",
    "KM-25HS-PT01-LYE-L": "KM-25HS-PT01-LYL-L",
    "KM-25SS-TS02-MOT-S": "KM-25SS-TS02-MOAT-S",
    "KM-25SS-TS02-MOT-M": "KM-25SS-TS02-MOAT-M",
    "KM-25SS-TS02-LYE-S": "KM-25SS-TS02-LYL-S",
    "KM-25SS-TS02-LYE-M": "KM-25SS-TS02-LYL-M",
    "KM-25SS-TS01-MGY-S": "KM-25SS-TS01-MGR-S",
    "KM-25SS-TS01-MGY-M": "KM-25SS-TS01-MGR-M",
    "KM-25SS-TS01-LYE-S": "KM-25SS-TS01-LYL-S",
    "KM-25SS-TS01-LYE-M": "KM-25SS-TS01-LYL-M",
}

processed_products = {}


def filter_tags(tags):
    tags = [
        tag
        for tag in tags
        if tag not in ["summer_sale_10%_off"]
        and not tag.startswith("2024 BF ")
        and not tag.startswith("2025 Holiday Season ")
    ]
    return tags


df = pd.read_excel(
    r"/Users/taro/Downloads/\(KUME\)\ Japan\ Shopify\ Sale\ List\ \(0804-0825\)_250725.xlsx".replace(
        "\\", ""
    ),
    header=3,
)
# for i, sku in enumerate(df[['Product Code']].values):
#     if sku == 'KM-25SS-TS02-MOT-S':
#         break
i = 0
for sku, percentage in df[["Product Code", "Final\nDiscount Rate"]].values[i:]:
    print(f"{sku} {percentage:.0%}")
    if sku in to_be_added_skus:
        continue
    sku = sku_map.get(sku, sku)
    product_id = client.product_id_by_sku(sku)
    product = client.product_by_id(product_id)
    tags = filter_tags(product["tags"]) + [f"{percentage:.0%}"]
    if product_id in processed_products:
        try:
            assert set(tags) == set(
                processed_products[product_id]
            ), f'tags are different amongst a product: {product_id}, {product["title"]}, {processed_products[product_id]} - {tags}'
        except AssertionError as e:
            print(e)
    else:
        processed_products[product_id] = tags
    client.update_product_tags(product_id, ",".join(tags))
