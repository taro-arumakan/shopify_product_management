import utils

client = utils.client("apricot-studios")
anims = ["TOGOM", "TITI", "BAMRONG"]

# for anim in anims:
#     copy_from = client.product_by_title(f'ANG {anim}')
#     copy_to = client.product_by_title(f'Newborn Comfort Kit - {anim}')
#     medias = copy_from['media']['nodes']
#     for media in medias:
#         client.assign_existing_image_to_products_by_id(media_id=media['id'], product_ids=[copy_to['id']])

copy_from = client.product_by_title("GRACE DIAPER CHANGE PAD")
for anim in anims:
    copy_to = client.product_by_title(f"Newborn Comfort Kit - {anim}")
    medias = copy_from["media"]["nodes"]
    for media in medias:
        client.assign_existing_image_to_products_by_id(
            media_id=media["id"], product_ids=[copy_to["id"]]
        )
