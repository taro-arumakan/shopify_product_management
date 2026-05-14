import utils

client = utils.client("asheis")

product_images_parent_dir = (
    "https://drive.google.com/drive/folders/1p7XAlJJEibinkDnn47hcfSkld783-i0D"
)
look_images_parent_dir = (
    "https://drive.google.com/drive/folders/1x8DuFlT03AF75XZDOiJ7mzGQ3CAHJ4TB"
)

product_dirs = client.list_folders(product_images_parent_dir.rsplit("/", 1)[-1])
print(len(product_dirs))

for p in product_dirs[:2]:
    print(p["name"])
    look_dir = client.find_by_folder_id_by_name(
        look_images_parent_dir.rsplit("/", 1)[-1], p["name"], exact_name=False
    )

    print(client.get_drive_image_details(p["id"]))
    print(client.get_drive_image_details(look_dir["id"]))
    print()
