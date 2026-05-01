import utils
import pandas as pd

client = utils.client("alvana")
rows = client.worksheet_rows(
    "126SqEHiGbVnjCx48OHy4p_FNSAY8QEgbKu68CqYYhoM", "26SS Product Master"
)
df = pd.DataFrame(columns=rows[0], data=rows[1:])

df = df[df["カラー"] != ""]
fill_columns = ["商品名", "商品品番"]
df[fill_columns] = df[fill_columns].replace("", pd.NA)
df[fill_columns] = df[fill_columns].ffill()
df = df[["商品品番", "商品名", "カラー"]]


def find_product_dir(product_sku, product_color):
    product_folder = client.find_by_folder_id_by_name(
        parent_folder_id="1XIzCmfzOaL1O9rGhTl0HAvTbRwu4FMx4",
        item_name=product_sku,
        item_type="folder",
        exact_name=False,
    )
    color_folder = product_folder and client.find_by_folder_id_by_name(
        parent_folder_id=product_folder["id"],
        item_name=product_color,
        item_type="folder",
    )
    return color_folder


with open("/Users/taro/Downloads/alvana.txt", "w") as of:
    for _, row in df.iterrows():
        folder = find_product_dir(row["商品品番"], row["カラー"])
        line = "\t".join(
            [
                f"{row['商品品番']} {row['カラー']}",
                (folder and folder["webViewLink"]) or "",
            ]
        )
        of.write(f"{line}\n")
        print(line)
