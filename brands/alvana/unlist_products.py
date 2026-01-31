remains = [
    "LAMBSKIN LEATHER PARKA",
    "SILK 60S JUMPER",
    "SUMMER WOOL L/S TEE SHIRTS",
    "空紡 CLASSIC PK TEE SHIRTS",
    "空紡 S/S TEE SHIRTS",
    "空紡 TANK TOP TEE SHIRTS",
    "DUCK WOOL DETROIT PARKA",
    "DUCK WOOL SHORT JACKET",
    "CORDUROY TRACKER JACKET",
    "SHEEP SUEDE SHORT JACKET",
    "5G LAMS WOOL CREW KNIT",
    "5G LAMS WOOL ZIP UP KNIT",
    "BHRAT DENIM OVER EASY PANTS",
    "NATURAL TWILL EASY PANTS",
]


import utils

client = utils.client("alvana")
products = client.products_by_query()
for product in products:
    if product["title"] not in remains:
        print(f"putting to draft: {product['title']}")
        client.update_product_status(product["id"], "DRAFT")
