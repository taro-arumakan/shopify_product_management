import logging
import pathlib
from brands.kume.client import KumeClient
from helpers.exceptions import NoVariantsFoundException
from collections import defaultdict

logging.basicConfig(level=logging.INFO)


def group_skus_by_discount(sku_discount_pairs):
    discount_groups = defaultdict(list)
    
    for sku, discount in sku_discount_pairs:
        if isinstance(discount, (int, float)):
            discount_str = f"{int(discount * 100)}%"
        else:
            discount_str = str(discount).replace("％", "%").strip()
        
        if discount_str in ["30%", "20%", "15%"]:
            discount_groups[discount_str].append(sku)
    
    logging.info(f"Grouped SKUs: 30%={len(discount_groups['30%'])}, 20%={len(discount_groups['20%'])}, 15%={len(discount_groups['15%'])}")
    return discount_groups


def get_product_ids_from_skus(client, skus):
    product_ids = set()
    
    for sku in skus:
        try:
            product_ids.add(client.product_id_by_sku(sku))
        except NoVariantsFoundException:
            logging.warning(f"SKU not found: {sku}")
    
    return product_ids


def add_tag_to_products(client, product_ids, tag):
    for product_id in product_ids:
        try:
            product = client.product_by_id(product_id)
            tags = product["tags"]
            if tag not in tags:
                tags = tags + [tag]
                client.update_product_tags(product_id, ",".join(tags))
                logging.debug(f"Added tag '{tag}' to product {product_id}")
        except Exception as e:
            logging.error(f"Error adding tag to product {product_id}: {e}")


def add_50_percent_off_tag():
    client = KumeClient()
    target_skus = [
        "KM-24FW-SK05-BK-M", "KM-24FW-SK05-BK-S", "KM-24FW-OP03-BK-M", "KM-24FW-OP03-BK-S",
        "KM-24FW-OP02-BK-M", "KM-24FW-OP02-BK-S", "KM-24FW-BL05-BR-M", "KM-24FW-BL05-DBR-S",
    ]
    tag = "2025_fs_50%"
    
    product_ids = set()
    for sku in target_skus:
        try:
            product_ids.add(client.product_id_by_sku(sku))
        except NoVariantsFoundException:
            logging.warning(f"SKU not found: {sku}")
    
    for product_id in product_ids:
        try:
            product = client.product_by_id(product_id)
            tags = product["tags"]
            if tag not in tags:
                client.update_product_tags(product_id, ",".join(tags + [tag]))
        except Exception as e:
            logging.error(f"Error adding tag to product {product_id}: {e}")


def main():
    """
    ・1/9-25のシートのSKUにFINAL SALEのタグ付け、％ごとにタグ付け
    ・1/9-12のシートのSKUに50% OFFのタグ付け
    ・コレクション作成 - FINAL SALE (tag == FINAL SALE)
    ・コレクション作成 - 50% OFF (tag == 50% OFF)
    """
    excel_file = pathlib.Path("/Users/kimotokentaro/Downloads") / "(KUME) Japan Shopify Sale List_FW SEASON OFF (0109-0125)_251217.xlsx"
    
    client = KumeClient()

    sku_discount_pairs = client.get_skus_from_excel(
        excel_file,
        header_row=4,  # 5行目（0ベース）がヘッダー行
        sku_column=1,  # B列
        discount_column=6,  # G列
    )
    
    discount_groups = group_skus_by_discount(sku_discount_pairs)
    print(discount_groups)
    # 全ての商品に「FINAL SALE」タグと％ごとのタグを付与
    for discount_rate, skus in discount_groups.items():
        product_ids = get_product_ids_from_skus(client, skus)
        add_tag_to_products(client, product_ids, "FINAL SALE")
        # ％ごとのタグ付け: 2025_fs_30%, 2025_fs_20%, 2025_fs_15%
        discount_tag = f"2025_fs_{discount_rate}"
        add_tag_to_products(client, product_ids, discount_tag)
    
    add_50_percent_off_tag()
    
    client.collection_create_by_tag("FINAL SALE", "FINAL SALE")
    client.collection_create_by_tag("50% OFF", "50% OFF")


if __name__ == "__main__":
    main()
