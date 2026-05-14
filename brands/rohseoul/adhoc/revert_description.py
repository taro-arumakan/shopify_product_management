import logging
import pandas as pd
import re
import utils

logging.basicConfig(level=logging.INFO)
korean_pattern = re.compile(r"[\uac00-\ud7a3]")


def revert_to_backup(client: utils.Client, df: pd.DataFrame, handle: str):
    backup = df[df["Handle"] == handle]["Body (HTML)"].iloc[0]
    logging.info(f"Reverting {handle} to backup")
    product_id = client.product_id_by_handle(handle)
    client.update_product_description(product_id, backup)


def main():
    df = pd.read_csv("/Users/taro/Downloads/20250513_rohseoul_products_export_1.csv")
    df = df[df["Title"].notnull()]
    client = utils.client("rohseoul")
    queries = [
        (client.products_by_tag, "shoulder bag"),
        (client.products_by_query, "tag_not:'shoulder bag'"),
    ]
    for query_func, param in queries:
        products = query_func(param, additional_fields=["descriptionHtml"])
        for product in products:
            if korean_pattern.search(product["descriptionHtml"]):
                revert_to_backup(client, df, product["handle"])


if __name__ == "__main__":
    main()
