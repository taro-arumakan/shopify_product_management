import utils

client = utils.client("alvana")

product_master = client.product_inputs_by_sheet_name("Product Master")
pm25aw = client.product_inputs_by_sheet_name("25AW Product Master")

pm_titles = [pi["title"] for pi in product_master]
pm25aw_titles = [pi["title"] for pi in pm25aw]


titles_pm_only = set(pm_titles) - set(pm25aw_titles)
print("Title - Product Master only:")

for t in titles_pm_only:
    print(t)
print()

titles_pm25aw_only = set(pm25aw_titles) - set(pm_titles)
print("Title - 25AW Product Master only:")
for t in titles_pm25aw_only:
    print(t)
print()

products_product_master = [
    p
    for p in product_master
    if all(
        p["title"] not in titles_list
        for titles_list in (titles_pm_only, titles_pm25aw_only)
    )
]
products_product_master_25aw = [
    p
    for p in pm25aw
    if all(
        p["title"] not in titles_list
        for titles_list in (titles_pm_only, titles_pm25aw_only)
    )
]
comparing_titles = set(p["title"] for p in products_product_master)
comparing_titles.update(p["title"] for p in products_product_master_25aw)

print("comparing these products")
for title in comparing_titles:
    print(title)
print()

for title in sorted(comparing_titles):
    product_pm = [p for p in products_product_master if p["title"] == title][0]
    product_pm_25 = [p for p in products_product_master_25aw if p["title"] == title][0]

    pm_skus = [o2["sku"] for o1 in product_pm["options"] for o2 in o1["options"]]
    pm25aw_skus = [o2["sku"] for o1 in product_pm_25["options"] for o2 in o1["options"]]
    if set(pm_skus) != set(pm25aw_skus):
        skus_pm_only = set(pm_skus) - set(pm25aw_skus)
        if skus_pm_only:
            print(f"{title} - SKU - Product Master only")
            for sku in sorted(skus_pm_only):
                try:
                    found = client.variant_by_sku(sku)
                except Exception as e:
                    found = False
                print(f"{sku}\t{bool(found)}")
        skus_pm25aw_only = set(pm25aw_skus) - set(pm_skus)
        if skus_pm25aw_only:
            print(f"{title} - SKU - 25AW Product Master only")
            for sku in sorted(skus_pm25aw_only):
                try:
                    found = client.variant_by_sku(sku)
                except Exception as e:
                    found = False
                print(f"{sku}\t{bool(found)}")
