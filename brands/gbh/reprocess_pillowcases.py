import logging
from brands.gbh.client import GbhHomeClient

logging.basicConfig(level=logging.INFO)


client = GbhHomeClient(use_simple_size_format=True)
client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False

product = client.product_by_title("GBH HOME PILLOWCASE (2 SIZES)")
client.archive_product(product)

client.sanity_check_sheet("PILLOWCASE 修正")
client.process_sheet_to_products(
    sheet_name="PILLOWCASE 修正",
)

product_info_list = client.product_info_list_from_sheet("PILLOWCASE 修正")
skus = [
    v2["sku"] for p in product_info_list for v1 in p["options"] for v2 in v1["options"]
]
variants = [client.variant_by_sku(sku) for sku in skus]
new_prices_by_variant_id = {
    variant["id"]: int(int(variant["compareAtPrice"]) * 0.9) for variant in variants
}

client.update_variant_prices_by_dict(
    variants=variants, new_prices_by_variant_id=new_prices_by_variant_id, testrun=True
)
