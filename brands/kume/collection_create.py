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
        "M-KM-26SS-TS04-CH-M",
        "M-KM-26SS-TS04-CH-L",
        "M-KM-26SS-TS04-CH-XL",
        "M-KM-26SS-TS04-IV-M",
        "M-KM-26SS-TS04-IV-L",
        "M-KM-26SS-TS04-IV-XL",
        "M-KM-26SS-TS04-NV-M",
        "M-KM-26SS-TS04-NV-L",
        "M-KM-26SS-TS04-NV-XL",
        "M-KM-26SS-SW08BEM",
        "M-KM-26SS-SW08BEL",
        "M-KM-26SS-SW08GRM",
        "M-KM-26SS-SW08GRL",
        "M-KM-26SS-SW08OLM",
        "M-KM-26SS-SW08OLL",
        "M-KM-26SS-SW08ORM",
        "M-KM-26SS-SW08ORL",
        "M-KM-26SS-JP02CHL",
        "M-KM-26SS-JP02CHXL",
        "M-KM-26SS-BL11DGRL",
        "M-KM-26SS-BL11DGRXL",
        "M-KM-26SS-BL11IVL",
        "M-KM-26SS-BL11IVXL",
        "M-KM-26SS-BL10LGRM",
        "M-KM-26SS-BL10LGRL",
        "M-KM-26SS-BL10LGRXL",
        "M-KM-26SS-BL10PKM",
        "M-KM-26SS-BL10PKL",
        "M-KM-26SS-BL10PKXL",
        "M-KM-25FW-PT06-BK-L",
        "M-KM-25FW-PT06-BK-M",
        "M-KM-25FW-PT06-BK-XL",
        "M-KM-25FW-PT06-MBL-L",
        "M-KM-25FW-PT06-MBL-M",
        "M-KM-25FW-PT06-MBL-XL",
        "KM-26SS-SW04BKS",
        "KM-26SS-SW04BKM",
        "KM-26SS-SW04BKL",
        "KM-26SS-SW04IVS",
        "KM-26SS-SW04IVM",
        "KM-26SS-SW04IVL",
        "KM-26SS-SW04MTS",
        "KM-26SS-SW04MTM",
        "KM-26SS-SW04MTL",
        "KM-26SS-SW01BKS",
        "KM-26SS-SW01BKM",
        "KM-26SS-SW01BKL",
        "KM-26SS-SW01IVS",
        "KM-26SS-SW01IVM",
        "KM-26SS-SW01IVL",
        "KM-26SS-SW01MTS",
        "KM-26SS-SW01MTM",
        "KM-26SS-SW01MTL",
        "KM-26SS-SK02ECS",
        "KM-26SS-SK02ECM",
        "KM-26SS-SK02ECL",
        "KM-26SS-SK02IVS",
        "KM-26SS-SK02IVM",
        "KM-26SS-SK02IVL",
        "KM-26SS-PT05IVS",
        "KM-26SS-PT05IVM",
        "KM-26SS-PT05IVL",
        "KM-26SS-PT05LBLS",
        "KM-26SS-PT05LBLM",
        "KM-26SS-PT05LBLL",
        "KM-26SS-PT04-CH-S",
        "KM-26SS-PT04-CH-M",
        "KM-26SS-PT04-CH-L",
        "KM-26SS-PT04-LKK-S",
        "KM-26SS-PT04-LKK-M",
        "KM-26SS-PT04-LKK-L",
        "KM-26SS-PT02-BK-S",
        "KM-26SS-PT02-BK-M",
        "KM-26SS-PT02-BK-L",
        "KM-26SS-OP01-IV-S",
        "KM-26SS-OP01-IV-M",
        "KM-26SS-OP01-IV-L",
        "KM-26SS-OP01-NV-S",
        "KM-26SS-OP01-NV-M",
        "KM-26SS-OP01-NV-L",
        "KM-26SS-JP01-CH-F",
        "KM-26SS-JP01-IV-F",
        "KM-26SS-JP01-OL-F",
        "KM-26SS-BL07-IV-S",
        "KM-26SS-BL07-IV-M",
        "KM-26SS-BL07-IV-L",
        "KM-26SS-BL05-BK-S",
        "KM-26SS-BL05-BK-M",
        "KM-26SS-BL05-BK-L",
        "KM-26SS-BL05-WH-S",
        "KM-26SS-BL05-WH-M",
        "KM-26SS-BL05-WH-L",
        "KM-25SS-SW06-BK-M",
        "KM-25SS-SW06-BK-S",
        "KM-25SS-SW06-IV-M",
        "KM-25SS-SW06-IV-S",
        "KM-25SS-SW06-LYE-M",
        "KM-25SS-SW06-LYE-S",
        "KM-25SS-SW06-MBE-M",
        "KM-25SS-SW06-MBE-S",
        "KM-25SS-SW04-LYE-S",
        "KM-25SS-SW04-LYE-M",
        "KM-25SS-SW04-IV-S",
        "KM-25SS-SW04-IV-M",
        "KM-25SS-SW04-MBE-S",
        "KM-25SS-SW04-MBE-M",
        "KM-25SS-SW03-LBL-S",
        "KM-25SS-SW03-LBL-M",
        "KM-25SS-SW03-WH-S",
        "KM-25SS-SW03-WH-M",
        "KM-25SS-SW03-BK-S",
        "KM-25SS-SW03-BK-M",
        "KM-25SS-SW03-LYE-S",
        "KM-25SS-SW03-LYE-M",
        "KM-25SS-SK04-IV-L",
        "KM-25SS-SK04-IV-M",
        "KM-25SS-SK04-IV-S",
        "KM-25SS-PT02-LYL-M",
        "KM-25SS-PT02-LYL-S",
        "KM-25SS-JP01-PC-S",
        "KM-25SS-JP01-PC-M",
        "KM-25SS-JK01-IV-M",
        "KM-25SS-JK01-IV-S",
        "KM-25SS-JK01-LBE-M",
        "KM-25SS-JK01-LBE-S",
        "KM-25SS-CT01-BE-F",
        "KM-25SS-BL06-IV-M",
        "KM-25SS-BL06-IV-S",
        "KM-25SS-BL06-NV-M",
        "KM-25SS-BL06-NV-S",
        "KM-25SS-BL04-WH-S",
        "KM-25SS-BL04-WH-M",
        "KM-25SS-BL01-WH-F",
        "KM-25SS-BL01-LM-F",
        "KM-25SS-BL01-SBL-F",
        "KM-25SS-BL01-PK-F",
        "KM-25SS-BG01-BK-F",
        "KM-25SS-BG01-WH-F",
        "KM-25SS-BG01-YL-F",
        "KM-25FW-SW02-CH-M",
        "KM-25FW-SW02-CH-S",
        "KM-25FW-SW02-DBN-M",
        "KM-25FW-SW02-DBN-S",
        "KM-25FW-SW02-LBL-M",
        "KM-25FW-SW02-LBL-S",
        "KM-25FW-SK04-BE-L",
        "KM-25FW-SK04-BE-M",
        "KM-25FW-SK04-BE-S",
        "KM-25FW-SK04-BK-L",
        "KM-25FW-SK04-BK-M",
        "KM-25FW-SK04-BK-S",
        "KM-25FW-JK01-TBK-M",
        "KM-25FW-JK01-TBK-S",
        "KM-25FW-JK01-BK-M",
        "KM-25FW-JK01-BK-S",
        "KM-25FW-BL02-BL-F",
    ]

    client = KumeClient()
    product_ids = {client.product_id_by_sku(sku) for sku in skus}
    client.collection_create_by_product_ids("3/30 New Lifestyle sale", product_ids)


def main():
    create_collection()


if __name__ == "__main__":
    main()
