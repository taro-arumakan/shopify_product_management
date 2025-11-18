import pandas as pd
import utils


def to_shopify_product_title(title, color):
    colors = map(str.strip, color.split("/"))
    initials = ["".join(c[0] for c in color.split(" ")) for color in colors]
    return f"{title} {'/'.join(initials)}"


def lookup_variant(client: utils.Client, sku, title, color):
    try:
        return client.variant_by_sku(sku)
    except utils.NoVariantsFoundException as ex:
        pass
    except utils.MultipleVariantsFoundException as ex:
        pass
    products = client.products_by_query(f"title:{title}*")
    colors = [color]
    if "POLARISED" in color:
        colors.append(color.replace("POLARISED", "POLARIZED"))

    for product in products:
        assert len(product["variants"]["nodes"]) == 1
        if product["variants"]["nodes"][0]["title"].upper() in colors:
            return product["variants"]["nodes"][0]


def main():
    client = utils.client("leisureallstars")
    df = pd.read_excel("/Users/taro/Downloads/SOH250711-EPOKHE-2.xlsx", header=10)
    df = df[df["スタイル"].notna()]
    df["not found"] = df["not found"].fillna(False)
    for style, color, sku, nf in df[
        ["スタイル", "カラー", "スタイルナンバー", "not found"]
    ].values.tolist():
        if not nf:
            # title = to_shopify_product_title(style.strip(), color.strip())
            variant = lookup_variant(client, sku.strip(), style.strip(), color.strip())
            if variant["sku"] != sku:
                print(f"update {style} - {color}: {variant['sku']} to {sku}")
                variant_id = variant["id"]
                product_id = client.product_id_by_variant_id(variant_id)
                client.update_variant_sku_by_variant_id(product_id, [variant_id], [sku])


if __name__ == "__main__":
    main()
