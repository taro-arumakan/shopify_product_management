import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArchiveAndRemoveVariant:

    def variant_to_archive_product(self, product_id, variant, option_name):
        archiving_color_option = set(
            [
                so["value"]
                for so in variant["selectedOptions"]
                if so["name"] == option_name
            ]
        )
        assert (
            len(archiving_color_option) == 1
        ), f"Expected exactly one option value for {option_name}, got {archiving_color_option}"
        archiving_color_option = list(archiving_color_option)[0]

        res = self.duplicate_product(
            product_id=product_id,
            new_title=f"{variant['product']['title']} - {variant['title']}",
            include_images=True,
            new_status="ARCHIVED",
        )
        archiving_product = res["productDuplicate"]["newProduct"]

        archiving_product_id = archiving_product["id"]
        logger.info(f"Duplicated product ID: {archiving_product_id}")

        new_variants = archiving_product["variants"]["nodes"]
        variant_ids_to_keep = [
            v["id"]
            for v in new_variants
            if any(
                so["name"] == option_name and so["value"] == archiving_color_option
                for so in v["selectedOptions"]
            )
        ]
        variant_ids_to_remove = [
            v["id"] for v in new_variants if v["id"] not in variant_ids_to_keep
        ]
        logger.debug("Removing other variants from the archived product")
        self._remove_unrelated_medias(archiving_product_id, variant_ids_to_keep)
        self.remove_product_variants(archiving_product_id, variant_ids_to_remove)

    def archive_and_remove_variants(self, variant_ids, option_name="カラー"):
        variants = [
            self.variant_by_variant_id(variant_id) for variant_id in variant_ids
        ]
        product_ids = set([variant["product"]["id"] for variant in variants])
        assert len(product_ids) == 1, "All variants must belong to the same product"
        product_id = list(product_ids)[0]

        product = self.product_by_id(product_id)

        variant_ids_to_remove = variant_ids
        variant_ids_to_keep = [
            v["id"]
            for v in product["variants"]["nodes"]
            if v["id"] not in variant_ids_to_remove
        ]

        if product["status"] == "ARCHIVED":
            assert (
                not variant_ids_to_keep
            ), f"Product ID: {product_id} is archived but has variants to keep: {variant_ids_to_keep}"
            logger.info(f"Product ID: {product_id} is already archived. Skipping.")

        elif not variant_ids_to_keep:
            logger.info(
                f"No variants left in product ID: {product_id}, archiving the product"
            )
            self.update_product_status(product_id, "ARCHIVED")

        else:
            for variant in variants:
                logger.info(
                    f"Archiving variant ID: {variant['id']} to a new archive product"
                )
                self.variant_to_archive_product(product_id, variant, option_name)

            logger.info(
                f"Removing variant IDs: {variant_ids} from product ID: {product_id}"
            )
            self._remove_unrelated_medias(product_id, variant_ids_to_keep)
            self.remove_product_variants(product_id, variant_ids_to_remove)
        for variant in variants:
            self.disable_inventory_tracking_by_sku(variant["sku"])

    def archive_and_remove_variant_by_skus(self, skus, option_name="カラー"):
        variants = [self.variant_by_sku(sku, active_only=False) for sku in skus]
        self.archive_and_remove_variants(
            [variant["id"] for variant in variants], option_name
        )


def main():
    import utils

    client = utils.client("rohseoul")
    import pandas as pd

    df = pd.read_csv(
        "/Users/taro/Downloads/ROH SEOUL Japan EC Product Details - 20250917_discontinued.csv"
    )
    grouped = (
        df.groupby("Handle", sort=False)["SKU"].apply(list).reset_index(name="SKU_List")
    )
    skus_by_handle = grouped.set_index("Handle")["SKU_List"].to_dict()
    handles = list(skus_by_handle.keys())
    handles = handles[handles.index("pulpy-hobo-bag-Nylon -1") :]
    for handle, skus in skus_by_handle.items():
        if handle in handles:
            logger.info(f"Processing handle: {handle} with SKUs: {skus}")
            client.archive_and_remove_variant_by_skus(skus, option_name="カラー")


if __name__ == "__main__":
    main()
