import logging
import re

logger = logging.getLogger(__name__)


class Variants:
    def update_a_variant_attributes(
        self, product_id, variant_id, attribute_names, attribute_values
    ):
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
        res = self.run_query(query, variables)
        return res["productVariantsBulkUpdate"]

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
        query = """
            mutation ProductVariantsCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
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
        variables = {
            "productId": product_id,
            "variants": [
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
            ],
        }
        return self.run_query(query, variables)
