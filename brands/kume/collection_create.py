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


def create_collection_by_excel():
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

def create_collection():

    skus = [
        "KM-26SS-JK01-IV-S",
        "KM-26SS-JK01-IV-M",
        "KM-26SS-JP01-IV-F",
        "KM-26SS-JP01-OL-F",
        "KM-26SS-JP01-CH-F",
        "M-KM-26SS-JP02GRL",
        "M-KM-26SS-JP02GRXL",
        "M-KM-26SS-JP02CHL",
        "M-KM-26SS-JP02CHXL",
        "M-KM-26SS-TS04-IV-M",
        "M-KM-26SS-TS04-IV-L",
        "M-KM-26SS-TS04-IV-XL",
        "M-KM-26SS-TS04-OAT-M",
        "M-KM-26SS-TS04-OAT-L",
        "M-KM-26SS-TS04-OAT-XL",
        "M-KM-26SS-TS04-CH-M",
        "M-KM-26SS-TS04-CH-L",
        "M-KM-26SS-TS04-CH-XL",
        "M-KM-26SS-TS04-NV-M",
        "M-KM-26SS-TS04-NV-L",
        "M-KM-26SS-TS04-NV-XL",
        "KM-26SS-BL07-IV-S",
        "KM-26SS-BL07-IV-M",
        "KM-26SS-BL07-IV-L",
        "M-KM-26SS-BL10LGRM",
        "M-KM-26SS-BL10LGRL",
        "M-KM-26SS-BL10LGRXL",
        "M-KM-26SS-BL10PKM",
        "M-KM-26SS-BL10PKL",
        "M-KM-26SS-BL10PKXL",
        "M-KM-26SS-BL11IVL",
        "M-KM-26SS-BL11IVXL",
        "M-KM-26SS-BL11DGRL",
        "M-KM-26SS-BL11DGRXL",
        "KM-26SS-SW01IVS",
        "KM-26SS-SW01IVM",
        "KM-26SS-SW01IVL",
        "KM-26SS-SW01MTS",
        "KM-26SS-SW01MTM",
        "KM-26SS-SW01MTL",
        "KM-26SS-SW01BKS",
        "KM-26SS-SW01BKM",
        "KM-26SS-SW01BKL",
        "KM-26SS-SW04IVS",
        "KM-26SS-SW04IVM",
        "KM-26SS-SW04IVL",
        "KM-26SS-SW04MTS",
        "KM-26SS-SW04MTM",
        "KM-26SS-SW04MTL",
        "KM-26SS-SW04BKS",
        "KM-26SS-SW04BKM",
        "KM-26SS-SW04BKL",
        "M-KM-26SS-SW08BEM",
        "M-KM-26SS-SW08BEL",
        "M-KM-26SS-SW08ORM",
        "M-KM-26SS-SW08ORL",
        "M-KM-26SS-SW08OLM",
        "M-KM-26SS-SW08OLL",
        "M-KM-26SS-SW08GRM",
        "M-KM-26SS-SW08GRL",
        "KM-26SS-SK02ECS",
        "KM-26SS-SK02ECM",
        "KM-26SS-SK02ECL",
        "KM-26SS-SK02IVS",
        "KM-26SS-SK02IVM",
        "KM-26SS-SK02IVL",
        "KM-26SS-SK03IVS",
        "KM-26SS-SK03IVM",
        "KM-26SS-SK03IVL",
        "KM-26SS-PT05IVS",
        "KM-26SS-PT05IVM",
        "KM-26SS-PT05IVL",
        "KM-26SS-PT05LBLS",
        "KM-26SS-PT05LBLM",
        "KM-26SS-PT05LBLL",
        "M-KM-26SS-PT07ECM",
        "M-KM-26SS-PT07ECL",
        "M-KM-26SS-PT07ECXL",
        "M-KM-26SS-PT07BEM",
        "M-KM-26SS-PT07BEL",
        "M-KM-26SS-PT07BEXL",
        "M-KM-26SS-PT07CHM",
        "M-KM-26SS-PT07CHL",
        "M-KM-26SS-PT07CHXL",
    ]

    client = KumeClient()
    product_ids = {client.product_id_by_sku(sku) for sku in skus}
    client.collection_create_by_product_ids("26ss 1st drop sale (2/6~2/15) ", product_ids)

def main():
    create_collection()

if __name__ == "__main__":
    main()
