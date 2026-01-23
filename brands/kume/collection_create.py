import logging
import pathlib
from brands.kume.client import KumeClient
from helpers.exceptions import NoVariantsFoundException
from collections import defaultdict

logging.basicConfig(level=logging.INFO)


def group_skus_by_discount(sku_discount_pairs):
    discount_groups = defaultdict(list)
    
    for sku, discount in sku_discount_pairs:
        if isinstance(discount, float):
            discount_str = f"{int(discount * 100)}%"
        else:
            discount_str = str(discount).replace("％", "%").strip()
        
        if discount_str in ["40%", "30%", "20%", "15%", "10%"]:
            discount_groups[discount_str].append(sku)

    return discount_groups


def get_product_ids_from_skus(client, skus):
    product_ids = set()
    
    for sku in skus:
        product_ids.add(client.product_id_by_sku(sku))

    return product_ids


def add_tag_to_products(client, product_ids, tag):
    for product_id in product_ids:
        product = client.product_by_id(product_id)
        tags = product["tags"]
        if tag not in tags:
            tags = tags + [tag]
            client.update_product_tags(product_id, ",".join(tags))


def main():
    excel_file = pathlib.Path("/Users/kimotokentaro/Downloads") / "(KUME) Japan Shopify Sale List_early spring sale (0206-0215)_260116.xlsx"
    
    client = KumeClient()

    sku_discount_pairs = client.get_skus_from_excel(
        excel_file,
        header_row=4,  # 5行目（0ベース）がヘッダー行
        sku_column=1,  # B列
        discount_column=6,  # G列
    )
    
    discount_groups = group_skus_by_discount(sku_discount_pairs)
    all_product_ids = set()
    for discount_rate, skus in discount_groups.items():
        product_ids = get_product_ids_from_skus(client, skus)
        all_product_ids.update(product_ids)
        discount_tag = f"2026_SpringSale_{discount_rate}"
        add_tag_to_products(client, product_ids, discount_tag)
    
    client.collection_create_by_product_ids("2/6-2/15 Spring Sale", all_product_ids)


if __name__ == "__main__":
    main()
