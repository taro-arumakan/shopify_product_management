import logging
import re

logger = logging.getLogger(__name__)


class VariantsManagement:
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
                        {
                            option_name: option_value
                            for option_name, option_value in zip(
                                option_names, variant_option_values
                            )
                        }
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
