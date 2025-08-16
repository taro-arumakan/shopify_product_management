import logging


logger = logging.getLogger(__name__)


class MergeProductsAsVariants:

    @staticmethod
    def _media_id_by_url(url, medias):
        for media in medias:
            if url == media["image"]["url"]:
                return media["id"]

    def add_product_to_product_as_variants(
        self, target_product_id, product_id_to_add, location_name
    ):
        right = self.product_by_id(product_id_to_add)

        skus = [v["sku"] for v in right["variants"]["nodes"]]
        media_ids = [v["id"] for v in right["media"]["nodes"]]
        variant_media_ids = [
            self._media_id_by_url(v["image"]["url"], right["media"]["nodes"])
            for v in right["variants"]["nodes"]
        ]
        prices = [v["price"] for v in right["variants"]["nodes"]]
        option_names = [
            o["name"] for o in right["variants"]["nodes"][0]["selectedOptions"]
        ]
        location_id = self.location_id_by_name(location_name)

        option_valuess = []
        stocks = []
        for variant in right["variants"]["nodes"]:
            option_values = [o["value"] for o in variant["selectedOptions"]]
            option_valuess.append(option_values)
            stocks.append(variant["inventoryQuantity"])

        self.variants_add(
            target_product_id,
            skus,
            media_ids,
            variant_media_ids,
            option_names,
            option_valuess,
            prices,
            stocks,
            location_id,
        )

    def archive_product(self, product, new_product_handle=None):
        self.update_product_status(product["id"], "ARCHIVED")
        for variant in product["variants"]["nodes"]:
            self.update_variant_attributes(
                product_id=product["id"],
                variant_id=variant["id"],
                attribute_names=[],
                attribute_values=[],
                sku=f"archived-{variant['sku']}",
            )
            self.disable_inventory_tracking_by_sku(f"archived-{variant['sku']}")
        if new_product_handle:
            logger.info(f"Redirecting {product['handle']} to {new_product_handle}")
            self.create_url_redirect(
                f"/products/{product['handle']}", f"/products/{new_product_handle}"
            )

    def merge_products_as_variants(self, product_title, location_name):
        products = self.products_by_title(product_title)
        products = [p for p in products if p["status"] == "ACTIVE"]
        logger.info(f"Merging {len(products)} products")
        merged = self.duplicate_product(
            products[0]["id"],
            products[0]["title"],
            include_images=True,
            new_status="DRAFT",
        )
        new_product_id = merged["productDuplicate"]["newProduct"]["id"]
        new_product_handle = merged["productDuplicate"]["newProduct"]["handle"]
        logger.info(
            f"Merging into a new product {new_product_id}: {new_product_handle}"
        )
        rights = products[1:]
        for right in rights:
            self.add_product_to_product_as_variants(
                new_product_id, right["id"], location_name
            )

        logger.info(f"Activating the new product")
        self.update_product_status(new_product_id, "ACTIVE")

        logger.info(f"Archiving and untracking the old products. Adding redirects")
        for product in products:
            self.archive_product(product, new_product_handle)


def main():
    import utils

    logging.basicConfig(level=logging.INFO)
    client = utils.client("rohseoul")
    client.merge_products_as_variants("Classic tomboy shirt", "Shop location")


if __name__ == "__main__":
    main()
