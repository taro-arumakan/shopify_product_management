import utils

client = utils.client("alvana")

lines = []
product_sku_map = {"ALV-0177": "ALV-00177"}

for line in lines:
    line = product_sku_map.get(line, line)
    variants = client.product_variants_by_query(query_string=f"sku:{line}*")
    product_titles = set(v["product"]["title"] for v in variants)
    live_product_titles = [pt for pt in product_titles if "(no image)" not in pt]
    if not live_product_titles and product_titles:
        print(line)
        print(product_titles)
    elif not product_titles:
        print(line)
