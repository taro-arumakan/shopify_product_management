import re
import utils
import pandas as pd

client = utils.client("alvana")
sku_pattern = re.compile("ALV\\-\\d+")

product_dirs = client.list_folders("1XIzCmfzOaL1O9rGhTl0HAvTbRwu4FMx4")
dirs_by_product_by_color = {}
for product_dir in product_dirs:
    if product_dir["name"] in [
        "コモザワ　余った写真",
        "FADE BALLON FOOTBALL OVER TEE SHIRTS",
        "FADE VINTAGE RV CREWNECK SWEAT TEE",
    ]:
        continue
    product_sku = sku_pattern.match(product_dir["name"]).group()
    dirs_by_product_by_color[product_sku] = {}
    color_dirs = client.list_folders(product_dir["id"])
    for color_dir in color_dirs:
        dirs_by_product_by_color[product_sku][color_dir["name"]] = color_dir[
            "webViewLink"
        ]

with open("/Users/taro/Downloads/alvana.txt", "w") as of:

    for product_sku in sorted(dirs_by_product_by_color):
        for color, url in dirs_by_product_by_color[product_sku].items():
            line = "\t".join([f"{product_sku} {color}", url])
            of.write(f"{line}\n")
            print(line)
