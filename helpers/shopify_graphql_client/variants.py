import logging
import re

logger = logging.getLogger(__name__)


class Variants:
    def update_variant_attributes(
        self, product_id, variant_id, attribute_names, attribute_values, sku=None
    ):
        assert len(attribute_names) == len(
            attribute_values
        ), "attribute_names and attribute_values must have the same length"

        query = """
        mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
            productVariantsBulkUpdate(productId: $productId, variants: $variants) {
                product {
                    id
                }
                productVariants {
                    id
                    %s
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """ % "\n".join(
            attribute_names
        )
        variables = {
            "productId": self.sanitize_id(product_id),
            "variants": [
                {
                    "id": self.sanitize_id(variant_id, "ProductVariant"),
                    **{
                        attribute_name: attribute_value
                        for attribute_name, attribute_value in zip(
                            attribute_names, attribute_values
                        )
                    },
                }
            ],
        }
        if sku:
            variables["variants"][0].setdefault("inventoryItem", {})["sku"] = sku
        res = self.run_query(query, variables)
        return res["productVariantsBulkUpdate"]

    def update_variant_barcode_by_sku(self, sku, barcode):
        variant = self.variant_by_sku(sku)
        return self.update_variant_attributes(
            variant["product"]["id"], variant["id"], ["barcode"], [barcode]
        )

    def product_variants_bulk_create(self, product_id, variants):
        query = """
        mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
            productVariantsBulkCreate(productId: $productId, variants: $variants) {
                productVariants {
                    id
                    title
                    selectedOptions {
                        name
                        value
                    }
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """
        variables = {"productId": product_id, "variants": variants}
        res = self.run_query(query, variables)
        if errors := res["productVariantsBulkCreate"]["userErrors"]:
            raise RuntimeError(f"Product variants creation failed: {errors}")
        return res["productVariantsBulkCreate"]["productVariants"]

    def variants_add(
        self,
        product_id,
        skus,
        media_ids,
        variant_media_ids,
        option_names,
        variant_option_valuess,
        prices,
        stocks,
        location_id,
    ):
        for media_id in media_ids or []:
            logger.info(f"Assigning media ID {media_id} to product ID {product_id}")
            self.assign_existing_image_to_products_by_id(media_id, [product_id])
        variants = [
            {
                "optionValues": [
                    {"name": option_value, "optionName": option_name}
                    for option_name, option_value in zip(
                        option_names, variant_option_values
                    )
                ],
                "inventoryItem": {
                    "sku": sku,
                    "tracked": True,
                },
                "mediaId": variant_media_id,
                "price": price,
                "inventoryQuantities": {
                    "availableQuantity": stock,
                    "locationId": location_id,
                },
            }
            for variant_option_values, sku, variant_media_id, price, stock in zip(
                variant_option_valuess, skus, variant_media_ids, prices, stocks
            )
        ]
        return self.product_variants_bulk_create(product_id, variants)

    def remove_product_variants(self, product_id, variant_ids):
        query = """
        mutation bulkDeleteProductVariants($productId: ID!, $variantsIds: [ID!]!) {
            productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
                product {
                    id
                    title
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """
        variables = {
            "productId": self.sanitize_id(product_id),
            "variantsIds": variant_ids,
        }
        res = self.run_query(query, variables)
        if res["productVariantsBulkDelete"]["userErrors"]:
            raise RuntimeError(
                f"Failed to remove variants: {res['productVariantsBulkDelete']['userErrors']}"
            )
        return res

    def update_variant_prices_by_dict(
        self, products, new_prices_by_variant_id, testrun=True
    ):
        # TODO: optimize bulk update - merge with update_variant_prices_by_variant_ids in product_attributes.py

        if testrun:
            logger.info("Test run mode - no prices will be updated")

        for p in products:
            logger.info(f"Processing product {p['id']} - {p['title']}")
            for variant in p["variants"]["nodes"]:
                current_price = int(variant["price"])
                new_price = new_prices_by_variant_id[variant["id"]]
                compare_at_price = variant["compareAtPrice"] or variant["price"]
                logger.info(
                    f"Updating price of {variant['id']} from {current_price} to {new_price}"
                )
                if not testrun:
                    self.update_variant_attributes(
                        product_id=p["id"],
                        variant_id=variant["id"],
                        attribute_names=["price", "compareAtPrice"],
                        attribute_values=[str(new_price), str(compare_at_price)],
                    )

    def revert_variant_prices(self, products, testrun=True):
        new_prices_by_variant_id = {
            v["id"]: int(v["compareAtPrice"])
            for p in products
            for v in p["variants"]["nodes"]
        }
        return self.update_variant_prices_by_dict(
            products, new_prices_by_variant_id, testrun
        )
