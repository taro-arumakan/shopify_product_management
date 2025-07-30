import utils

client = utils.client("kumej")

tags_to_remove = [
    "2024 BF 20% OFF",
    "2025 Holiday Season 20% OFF",
    "2025 Holiday Season 30% OFF",
    "2025 Holiday Season 5% OFF",
    "2025-02-20",
    "2025-03-10",
    "3/31             (3RD DROP)",
    "5/30             (HOT SUMMER)",
    "9/19/2024",
    "summer_sale_10%_off",
]

tags_to_update = {
    "Bottoms": "BOTTOM",
    "Dresses": "DRESS",
    "SHIRTS &BLOUSE": "SHIRTS & BLOUSE",
    "Tops": "TOP",
}

all_tags = {
    "2024 BF 20% OFF",
    "2025 Holiday Season 20% OFF",
    "2025 Holiday Season 30% OFF",
    "2025 Holiday Season 5% OFF",
    "2025-02-20",
    "2025-03-10",
    "2025_summer_outlet",
    "25SS-HOTSUMMER",
    "3/31             (3RD DROP)",
    "5/30             (HOT SUMMER)",
    "9/19/2024",
    "ACC",
    "BAG",
    "BOTTOM",
    "Bag",
    "Bottoms",
    "COAT",
    "DELICAT",
    "DENIM",
    "DRESS",
    "Dresses",
    "ESSENTIAL",
    "ETC",
    "FW23",
    "FW24",
    "HAPPY BAG",
    "HATS",
    "Hankyu Exclusive",
    "JACKET",
    "JOLI",
    "JUMPER",
    "KEICA10",
    "LACHE",
    "New Arrival",
    "OUTER",
    "PANTS",
    "SHIRTS & BLOUSE",
    "SHIRTS &BLOUSE",
    "SKIRT",
    "SS24",
    "SUMMER 23",
    "SUMMER 24",
    "SUMMER 25",
    "SWEATER",
    "T-SHIRT & MTM",
    "TOP",
    "Tops",
    "best",
    "summer_sale_10%_off",
}

product_ids = set()
for tag in tags_to_remove:
    product_ids.update([p["id"] for p in client.products_by_query(f"tag:'{tag}'")])

for tag in tags_to_update:
    product_ids.update([p["id"] for p in client.products_by_query(f"tag:'{tag}'")])

print(len(product_ids))

for product_id in product_ids:
    product = client.product_by_id(product_id)
    tags = [
        tags_to_update.get(t, t) for t in product["tags"] if t not in tags_to_remove
    ]
    client.update_product_tags(product_id, ",".join(tags))
