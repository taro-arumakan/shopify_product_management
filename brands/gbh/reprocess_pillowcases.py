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
