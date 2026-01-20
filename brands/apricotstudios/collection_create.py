import logging
import pathlib
import utils
from helpers.exceptions import NoVariantsFoundException
from collections import defaultdict

logging.basicConfig(level=logging.INFO)


def group_skus_by_discount(sku_discount_pairs):
    """SKUを割引率ごとにグループ化"""
    discount_groups = defaultdict(list)
    
    for sku, discount in sku_discount_pairs:
        if isinstance(discount, float):
            discount_str = f"{int(discount * 100)}%"
        else:
            discount_str = str(discount).replace("％", "%").strip()
        
        if discount_str in ["30%", "20%", "15%", "10%"]:
            discount_groups[discount_str].append(sku)
    
    logging.info(f"Grouped SKUs by discount: {dict((k, len(v)) for k, v in discount_groups.items())}")
    return discount_groups


def get_product_ids_from_skus(client, skus):
    """SKUリストから商品IDセットを取得"""
    product_ids = set()
    
    for sku in skus:
        try:
            product_ids.add(client.product_id_by_sku(sku))
        except NoVariantsFoundException:
            logging.warning(f"SKU not found: {sku}")
    
    return product_ids


def add_tag_to_products(client, product_ids, tag):
    """商品にタグを追加"""
    for product_id in product_ids:
        try:
            product = client.product_by_id(product_id)
            tags = product["tags"]
            if tag not in tags:
                tags = tags + [tag]
                client.update_product_tags(product_id, ",".join(tags))
                logging.info(f"Added tag '{tag}' to product {product_id}")
        except Exception as e:
            logging.error(f"Error adding tag to product {product_id}: {e}")


def main():

    excel_file = pathlib.Path("/Users/kimotokentaro/Downloads") / "【Apriot Studios】25Autumn&Winter Season Off Event.xlsx"
    
    client = utils.client("apricot-studios")

    sku_discount_pairs = client.get_skus_from_excel(
        excel_file,
        header_row=7,
        sku_column=12,  # M列（SKU）
        discount_column=17,  # R列（割引率）
    )
    
    discount_groups = group_skus_by_discount(sku_discount_pairs)
    
    all_product_ids = set()
    for discount_rate, skus in discount_groups.items():
        product_ids = get_product_ids_from_skus(client, skus)
        print(product_ids)
        all_product_ids.update(product_ids)
        
        add_tag_to_products(client, product_ids, "2026 Season Off Sale")
        
        discount_tag = f"2026_season_off_sale_{discount_rate}"
        add_tag_to_products(client, product_ids, discount_tag)
    
    client.collection_create_by_tag(
        "26 Autumn & Winter Season Off Event",
        "2026 Season Off Sale"
    )

if __name__ == "__main__":
    main()
