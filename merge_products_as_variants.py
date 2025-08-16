import utils

client = utils.client("rohseoul")

products = client.products_by_title("Mini pulpy hobo bag")
location_name = "Shop location"

merged = client.duplicate_product(
    products[0]["id"], "TEST - Mini pulpy hobo bag", True, "DRAFT"
)
rights = products[1:]


def media_id_by_url(url, medias):
    for media in medias:
        if url == media["image"]["url"]:
            return media["id"]


def add_product_to_product_as_variants(target_product_id, product_id_to_add):
    right = client.product_by_id(product_id_to_add)

    skus = [v["sku"] for v in right["variants"]["nodes"]]
    media_ids = [v["id"] for v in right["media"]["nodes"]]
    variant_media_ids = [
        media_id_by_url(v["image"]["url"], right["media"]["nodes"])
        for v in right["variants"]["nodes"]
    ]
    prices = [v["price"] for v in right["variants"]["nodes"]]
    option_names = [o["name"] for o in right["variants"]["nodes"][0]["selectedOptions"]]
    location_id = client.location_id_by_name(location_name)

    option_valuess = []
    stocks = []
    for variant in right["variants"]["nodes"]:
        for on in option_names:
            option_values = [
                o["value"] for o in variant["selectedOptions"] if o["name"] == on
            ]
            option_valuess.append(option_values)
        stocks.append(variant["inventoryQuantity"])

    client.variants_add(
        target_product_id,
        skus,
        media_ids,
        variant_media_ids,
        option_names,
        option_valuess,
        prices,
        stocks,
        location_id,
    )


for right in rights:
    add_product_to_product_as_variants(
        merged["productDuplicate"]["newProduct"]["id"], right["id"]
    )
