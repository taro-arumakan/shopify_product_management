import pandas as pd
import utils


def main():
    client = utils.client("leisureallstars")
    df = pd.read_excel("/Users/taro/Downloads/SOH250711-EPOKHE-2.xlsx", header=10)
    df = df[df["スタイルナンバー"].notna()]
    df["割引率"] = df["割引率"].fillna(0.2)
    for sku, discount_rate in df[["スタイルナンバー", "割引率"]].values.tolist():
        # title = to_shopify_product_title(style.strip(), color.strip())
        try:
            variant = client.variant_by_sku(sku)
        except:
            print(f"variant not found for {sku}")
        else:
            original_price = int(variant["compareAtPrice"] or variant["price"])
            discount_price = int(original_price * (1 - discount_rate))
            print(
                f"going to update price of {variant['displayName']} from {original_price} to {discount_price}"
            )
            client.update_variant_price_by_variant_id(
                product_id=variant["product"]["id"],
                variant_ids=[variant["id"]],
                prices=[discount_price],
                compare_at_prices=[original_price],
            )


if __name__ == "__main__":
    main()
