import logging
import utils

logging.basicConfig(level=logging.INFO)

client = utils.client("archive-epke")

product_inputs = client.product_inputs_by_sheet_name("2025.7 SPOT Release")
product_inputs = [pr for pr in product_inputs if pr["title"] == "Knotted layer bag"]
product_input = product_inputs[0]

product_id = client.product_id_by_title(product_input["title"])
drive_links, skuss = client.populate_drive_ids_and_skuss(product_input)

# res = client.add_product_images(
#     product_id,
#     drive_links[0],
#     "/Users/taro/Downloads/archivépke20250710/",
#     f"upload_20250710_{skuss[0][0]}_",
# )

# new_media_id = [m['id'] for m in res[-1]["productCreateMedia"]["media"]]

new_media_ids = [
    "gid://shopify/MediaImage/36358461554909",
    "gid://shopify/MediaImage/36358461587677",
    "gid://shopify/MediaImage/36358461685981",
    "gid://shopify/MediaImage/36358461915357",
    "gid://shopify/MediaImage/36358461980893",
    "gid://shopify/MediaImage/36358462013661",
]

client.variants_add(
    product_id,
    skuss[0],
    [],
    [new_media_ids[0]],
    ["カラー", "サイズ"],
    [[product_input["options"][0]["カラー"], "FREE"]],
    [product_input["options"][0]["price"]],
    [product_input["options"][0]["stock"]],
    client.location_id_by_name("Archivépke Warehouse"),
)
