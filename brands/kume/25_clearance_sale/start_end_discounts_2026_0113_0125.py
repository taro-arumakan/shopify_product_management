from brands.kume.client import KumeClient
from helpers.exceptions import NoVariantsFoundException
import logging

logging.basicConfig(level=logging.INFO)


def start_end_discounts_2026_0113_0125(testrun=True, start_or_end="end"):
    client = KumeClient()
    target_skus = [
        "KM-24FW-SK05-BK-M", "KM-24FW-SK05-BK-S", "KM-24FW-OP03-BK-M", "KM-24FW-OP03-BK-S",
        "KM-24FW-OP02-BK-M", "KM-24FW-OP02-BK-S", "KM-24FW-BL05-BR-M", "KM-24FW-BL05-DBR-S",
    ]
    
    product_ids = set()
    for sku in target_skus:
        try:
            product_ids.add(client.product_id_by_sku(sku))
        except NoVariantsFoundException:
            logging.warning(f"SKU not found: {sku}")
    
    products = []
    for product_id in product_ids:
        try:
            product = client.product_by_id(product_id)
            products.append(product)
            tags = product["tags"]
            if "FINAL SALE" not in tags:
                client.update_product_tags(product_id, ",".join(tags + ["FINAL SALE"]))
        except Exception as e:
            logging.error(f"Error processing product {product_id}: {e}")
    
    if start_or_end == "end":
        client.revert_product_prices(products, testrun=testrun)
    else:
        new_prices_by_variant_id = {
            v["id"]: int(int(v["compareAtPrice"] or v["price"]) * 0.7)
            for p in products
            for v in p["variants"]["nodes"]
        }
        client.update_product_prices_by_dict(products, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun)


if __name__ == "__main__":
    start_end_discounts_2026_0113_0125()
