import logging
import pathlib
from brands.kume.client import KumeClient
from helpers.exceptions import NoVariantsFoundException
from collections import defaultdict

logging.basicConfig(level=logging.INFO)


def main():
    # Excelファイルのパスを指定（必要に応じて変更してください）
    # pathlib.Pathを使用して正しくパスを処理
    excel_file = pathlib.Path("/Users/kimotokentaro/Downloads") / "(KUME) Japan Shopify Sale List_Black Friday (1126-1130)_251107.xlsx"
    
    client = KumeClient()
    
    # ExcelファイルからSKUと割引%を取得
    # B列（インデックス1）からSKU、G列（インデックス6）から割引%を取得
    # 5行目（インデックス4）からデータ開始
    sku_discount_pairs = client.get_skus_from_excel(
        excel_file,
        sku_column=1,  # B列
        start_row=4,   # 5行目（0ベース）
        discount_column=6,  # G列
    )
    logging.info(f"Found {len(sku_discount_pairs)} SKU-discount pairs from Excel file")
    
    # # デバッグ: 最初の10件を表示
    # if sku_discount_pairs:
    #     logging.info(f"Sample data (first 10): {sku_discount_pairs[:10]}")
    
    # # 割引率でグループ分け（50%、20%、10%）
    # discount_groups = defaultdict(list)
    # unknown_discounts = defaultdict(list)
    
    # for sku, discount in sku_discount_pairs:
    #     # 割引%を正規化（「50%」「50」「50％」などに対応）
    #     discount_str = str(discount).replace("％", "%").strip()
        
    #     # 数値として解析を試みる（「50%」→ 50、「0.5」→ 50など）
    #     discount_value = None
    #     try:
    #         # 「50%」形式の場合
    #         if "%" in discount_str:
    #             discount_value = float(discount_str.replace("%", "").strip())
    #         # 数値形式の場合（0.5 = 50%）
    #         else:
    #             discount_value = float(discount_str) * 100
    #     except (ValueError, AttributeError):
    #         pass
        
    #     # 割引率でグループ分け
    #     if discount_value is not None:
    #         if abs(discount_value - 50) < 1:  # 50% ± 1%
    #             discount_groups["50%"].append(sku)
    #         elif abs(discount_value - 20) < 1:  # 20% ± 1%
    #             discount_groups["20%"].append(sku)
    #         elif abs(discount_value - 10) < 1:  # 10% ± 1%
    #             discount_groups["10%"].append(sku)
    #         else:
    #             unknown_discounts[discount_str].append(sku)
    #     else:
    #         # 文字列マッチング（フォールバック）
    #         discount_normalized = discount_str.lower()
    #         if "50%" in discount_normalized or discount_normalized == "50":
    #             discount_groups["50%"].append(sku)
    #         elif "20%" in discount_normalized or discount_normalized == "20":
    #             discount_groups["20%"].append(sku)
    #         elif "10%" in discount_normalized or discount_normalized == "10":
    #             discount_groups["10%"].append(sku)
    #         else:
    #             unknown_discounts[discount_str].append(sku)
    
    # # 不明な割引%をログに記録
    # if unknown_discounts:
    #     for discount, skus in unknown_discounts.items():
    #         logging.warning(f"Unknown discount '{discount}' for {len(skus)} SKUs (sample: {skus[:5]})")
    
    # logging.info(f"Grouped SKUs: 50%={len(discount_groups['50%'])}, 20%={len(discount_groups['20%'])}, 10%={len(discount_groups['10%'])}")
    
    # # 各グループに対してタグを付与
    # tag_mapping = {
    #     "50%": "2025 Black Friday Sale 50% OFF",
    #     "20%": "2025 Black Friday Sale 20% OFF",
    #     "10%": "2025 Black Friday Sale 10% OFF"
    # }
    
    # all_product_ids = set()
    
    # for discount_rate, skus in discount_groups.items():
    #     tag = tag_mapping[discount_rate]
    #     logging.info(f"Processing {discount_rate} group ({len(skus)} SKUs) with tag: {tag}")
        
    #     product_ids = set()
    #     not_found_skus = []
        
    #     for sku in skus:
    #         try:
    #             product_id = client.product_id_by_sku(sku)
    #             product_ids.add(product_id)
    #         except NoVariantsFoundException:
    #             not_found_skus.append(sku)
    #             logging.warning(f"SKU not found: {sku}")
        
    #     logging.info(f"Found {len(product_ids)} product IDs for {discount_rate} group")
    #     if not_found_skus:
    #         logging.warning(f"{len(not_found_skus)} SKUs not found in {discount_rate} group")
        
    #     # 全製品IDに追加
    #     all_product_ids.update(product_ids)
        
    #     # 各製品にタグを追加
    #     for product_id in product_ids:
    #         try:
    #             product = client.product_by_id(product_id)
    #             tags = product["tags"]
    #             # 既存のタグに新しいタグを追加（重複を避ける）
    #             if tag not in tags:
    #                 tags = tags + [tag]
    #                 client.update_product_tags(product_id, ",".join(tags))
    #                 logging.debug(f"Added tag '{tag}' to product {product_id}")
    #         except Exception as e:
    #             logging.error(f"Error adding tag to product {product_id}: {e}")
    
    # # コレクション作成（全グループの製品IDを集約）
    # logging.info(f"Total product IDs collected: {len(all_product_ids)}")
    # client.collection_create("2025 Black Friday Sale 11/26-11/30", all_product_ids)


if __name__ == "__main__":
    main()
