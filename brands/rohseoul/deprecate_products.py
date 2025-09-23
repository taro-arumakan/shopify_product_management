import logging
import pandas as pd
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    client = utils.client("rohseoul")
    df = pd.read_csv(
        "/Users/taro/Downloads/ROH SEOUL Japan EC Product Details - 20250917_discontinued.csv"
    )
    grouped = (
        df.groupby("Handle", sort=False)["SKU"].apply(list).reset_index(name="SKU_List")
    )
    skus_by_handle = grouped.set_index("Handle")["SKU_List"].to_dict()
    handles = list(skus_by_handle.keys())
    handles = handles[handles.index("pulpy-crossbody-bag-nylon") + 1 :]
    for handle, skus in skus_by_handle.items():
        if handle in handles:
            logger.info(f"Processing handle: {handle} with SKUs: {skus}")
            client.archive_and_remove_variant_by_skus(skus, option_name="カラー")


if __name__ == "__main__":
    main()
