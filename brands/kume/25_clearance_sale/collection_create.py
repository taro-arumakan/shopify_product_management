import logging
import pathlib
from brands.kume.client import KumeClient
from helpers.exceptions import NoVariantsFoundException
from collections import defaultdict

logging.basicConfig(level=logging.INFO)


def main():
    """
    ・1/9-25のシートのSKUにFINAL SALEのタグ付け、％ごとにタグ付け
    ・1/9-12のシートのSKUに50% OFFのタグ付け
    ・コレクション作成 - FINAL SALE (tag == FINAL SALE)
    ・コレクション作成 - 50% OFF (tag == 50% OFF)
    """
    excel_file = pathlib.Path("/Users/kimotokentaro/Downloads") / "(KUME) Japan Shopify Sale List_Black Friday (1126-1130)_251107.xlsx"
    
    client = KumeClient()

    sku_discount_pairs = client.get_skus_from_excel(
        excel_file,
        sku_column=1,  # B列
        start_row=4,   # 5行目（0ベース）
        discount_column=6,  # G列
    )
    logging.info(f"Found {len(sku_discount_pairs)} SKU-discount pairs from Excel file")
    
    # デバッグ: 最初の10件を表示
    if sku_discount_pairs:
        logging.info(f"Sample data (first 10): {sku_discount_pairs[:10]}")
    
    # 割引率でグループ分け（30%、20%、15%）
    discount_groups = defaultdict(list)
    unknown_discounts = defaultdict(list)
    
    for sku, discount in sku_discount_pairs:
        # 割引%を正規化（「30%」「30」「30％」などに対応）
        discount_str = str(discount).replace("％", "%").strip()
        
        discount_value = None
        try:
            discount_value = float(discount_str.replace("%", "").strip())
        except (ValueError, AttributeError):
            pass
        
        # 割引率でグループ分け
        if discount_value is not None:
            if abs(discount_value - 30) < 1:  # 30% ± 1%
                discount_groups["30%"].append(sku)
            elif abs(discount_value - 20) < 1:  # 20% ± 1%
                discount_groups["20%"].append(sku)
            elif abs(discount_value - 15) < 1:  # 15% ± 1%
                discount_groups["15%"].append(sku)
            else:
                unknown_discounts[discount_str].append(sku)
        else:
            discount_normalized = discount_str.lower()
            if "30%" in discount_normalized or discount_normalized == "30":
                discount_groups["30%"].append(sku)
            elif "20%" in discount_normalized or discount_normalized == "20":
                discount_groups["20%"].append(sku)
            elif "15%" in discount_normalized or discount_normalized == "15":
                discount_groups["15%"].append(sku)
            else:
                unknown_discounts[discount_str].append(sku)
    
    logging.info(f"Grouped SKUs: 30%={len(discount_groups['30%'])}, 20%={len(discount_groups['20%'])}, 15%={len(discount_groups['15%'])}")
    
    # 全ての商品に「FINAL SALE」タグを付与
    tag = "FINAL SALE"
    
    all_product_ids = set()
    
    for discount_rate, skus in discount_groups.items():
        logging.info(f"Processing {discount_rate} group ({len(skus)} SKUs)")
        
        product_ids = set()
        not_found_skus = []
        
        for sku in skus:
            try:
                product_id = client.product_id_by_sku(sku)
                product_ids.add(product_id)
            except NoVariantsFoundException:
                not_found_skus.append(sku)
                logging.warning(f"SKU not found: {sku}")
        
        logging.info(f"Found {len(product_ids)} product IDs for {discount_rate} group")
        if not_found_skus:
            logging.warning(f"{len(not_found_skus)} SKUs not found in {discount_rate} group")
        
        # 全製品IDに追加
        all_product_ids.update(product_ids)
        
        # 各製品にタグを追加
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
    
    # 指定SKUに「50% OFF」タグを付与
    add_50_percent_off_tag()

    # コレクション作成
    client.collection_create_by_tag("FINAL SALE", "FINAL SALE")
    client.collection_create_by_tag("50% OFF", "50% OFF")


def add_50_percent_off_tag():
    client = KumeClient()
    target_skus = [
        "KM-24FW-SK05-BK-M", "KM-24FW-SK05-BK-S", "KM-24FW-OP03-BK-M", "KM-24FW-OP03-BK-S",
        "KM-24FW-OP02-BK-M", "KM-24FW-OP02-BK-S", "KM-24FW-BL05-BR-M", "KM-24FW-BL05-DBR-S",
    ]
    tag = "50% OFF"
    
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


if __name__ == "__main__":
    main()
