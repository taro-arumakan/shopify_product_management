import pandas as pd
import utils

client = utils.client("gbh")

rows = client.worksheet_rows("1SzaDFzw513CA-vaGeAoRyd6N9eA_IwOg_JjdYSsSa9g", "시트1")
df = pd.DataFrame(rows[2:], columns=rows[1])

for sku, sheet_price in df[["BARCODE", "変更後\n値段(税込)"]].values:
    try:
        variant = client.variant_by_sku(sku)
    except utils.NoVariantsFoundException as ex:
        print(ex)
    else:
        current_price = int(variant["price"])
        sheet_price = int(sheet_price or 0)
        if current_price != sheet_price:
            print(f"price does not match: {sku}, {sheet_price}, {current_price}")
