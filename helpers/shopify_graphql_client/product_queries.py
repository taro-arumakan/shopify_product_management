import logging
import string
from helpers.exceptions import (
    MultipleProductsFoundException,
    NoProductsFoundException,
    MultipleVariantsFoundException,
    NoVariantsFoundException,
)

logger = logging.getLogger(__name__)

additional_punctuation_chars = "‘’“” "
punctuation_chrs = (
    "".join([s for s in string.punctuation if s not in ["-"]])
    + additional_punctuation_chars
)
punctuation_translator = str.maketrans("", "", punctuation_chrs)


class ProductQueries:
    """
    A class to handle GraphQL queries related to products in Shopify, inherited by the ShopifyGraphqlClient class.
    """

    @staticmethod
    def product_title_to_handle(title, handle_suffix=None):
        parts = title.lower().split(" ") + ([handle_suffix] if handle_suffix else [])
        parts = [part.translate(punctuation_translator) for part in parts]
        return "-".join(parts)

    def products_by_query(self, query_string, additional_fields=None):
        query = """
        query productsByQuery($query_string: String!) {
            products(first: 100, query: $query_string, sortKey: TITLE) {
                nodes {
                    id
                    title
                    handle
                    tags%s
                    metafields (first:10) {
                        nodes {
                            id
                            namespace
                            key
                            value
                        }
                    }
                    variants (first:10) {
                        nodes {
                            id
                            title
                            sku
                            price
                            compareAtPrice
                            selectedOptions {
                                name
                                value
                            }
                            image {
                                id
                                url
                            }
                        }
                    }
                    media (first:100) {
                        nodes {
                            id
                        }
                    }
                }
            }
        }
        """ % (
            f"\n{'\n'.join(additional_fields)}" if additional_fields else ""
        )
        variables = {"query_string": query_string}
        res = self.run_query(query, variables)
        res = res["products"]["nodes"]
        assert len(res) < 100, f"Too many products found for {query_string}: {len(res)}"
        return res

    def product_by_query(self, query_string, additional_fields=None):
        products = self.products_by_query(query_string, additional_fields)
        if len(products) != 1:
            raise (
                MultipleProductsFoundException if products else NoProductsFoundException
            )(
                f"{'Multiple' if products else 'No'} products found for {query_string}: {products}"
            )
        return products[0]

    def product_by_id(self, identifier, additional_fields=None):
        return self.products_by_query(
            f"id:'{identifier.rsplit('/', 1)[-1]}'", additional_fields
        )[0]

    def products_by_title(self, title, additional_fields=None):
        products = self.products_by_query(
            f"title:'{title.replace("'", "\\'")}'", additional_fields
        )
        if len(products) == 0:
            raise NoProductsFoundException(f"No products found for {title}")
        return products

    def product_ids_by_title(self, title):
        res = self.products_by_title(title)
        return [r["id"] for r in res]

    def product_by_title(self, title, additional_fields=None):
        return self.product_by_query(
            f"title:'{title.replace("'", "\\'")}'", additional_fields
        )

    def product_id_by_title(self, title):
        return self.product_by_title(title)["id"]

    def product_by_handle(self, handle, additional_fields=None):
        return self.product_by_query(f"handle:'{handle}'", additional_fields)

    def product_id_by_handle(self, handle):
        return self.product_by_handle(handle)["id"]

    def products_by_tag(self, tag, additional_fields=None):
        return self.products_by_query(f"tag:'{tag}'", additional_fields)

    def product_variants_by_query(self, query, filter_archived=True):
        query = (
            """
        {
            productVariants(first:100, query: "%s") {
                nodes {
                    id
                    title
                    displayName
                    sku
                    price
                    compareAtPrice
                    media (first:5){
                        nodes{
                            id
                            ... on MediaImage {
                                image{
                                    url
                                }
                            }
                        }
                    }
                    selectedOptions {
                        name
                        value
                    }
                    product {
                        id
                        title
                        status
                    }
                }
            }
        }
        """
            % query
        )
        res = self.run_query(query)
        res = res["productVariants"]["nodes"]
        if filter_archived:
            # Shopify API ignores product_status filter on productVariants query
            logger.debug("Filtering ARCHIVED products' variants")
            res = [r for r in res if r["product"]["status"] != "ARCHIVED"]
        return res

    def product_variants_by_product_id(self, product_id):
        product_id = self.sanitize_id(product_id)
        product_id = product_id.rsplit("/", 1)[-1]
        return self.product_variants_by_query(f"product_id:{product_id}")

    def product_variants_by_tag(self, tag):
        return self.product_variants_by_query(f"tag:'{tag}'")

    def variant_by_variant_id(self, variant_id):
        variant_id = self.sanitize_id(variant_id, "ProductVariant").rsplit("/", 1)[-1]
        if len(res := self.product_variants_by_query(f"id:{variant_id}")) != 1:
            raise (MultipleVariantsFoundException if res else NoVariantsFoundException)(
                f"{'Multiple' if res else 'No'} variants found for {variant_id}: {res}"
            )
        return res[0]

    def variant_by_sku(self, sku, active_only=True):
        if (
            len(
                res := self.product_variants_by_query(
                    f"sku:{sku}", filter_archived=active_only
                )
            )
            != 1
        ):
            if res and active_only:
                logger.info("Filtering non-active products' variants")
                res = [r for r in res if r["product"]["status"] == "ACTIVE"]
            if len(res) != 1:
                raise (
                    MultipleVariantsFoundException if res else NoVariantsFoundException
                )(f"{'Multiple' if res else 'No'} variants found for {sku}: {res}")
        return res[0]

    def variant_id_by_sku(self, sku, active_only=True):
        return self.variant_by_sku(sku, active_only=active_only)["id"]

    def product_id_by_variant_id(self, variant_id):
        variant = self.variant_by_variant_id(variant_id)
        return variant["product"]["id"]

    def product_id_by_sku(self, sku, active_only=True):
        variant = self.variant_by_sku(sku, active_only=active_only)
        return variant["product"]["id"]

    def products_by_collection_handle(self, collection_handle):
        query = """
            query getCollectionByHandle($collection_handle: String!) {
                collectionByHandle(handle: $collection_handle) {
                    id
                    title
                    products(first: 100) {
                        nodes {
                            id
                            title
                            tags
                        }
                    }
                }
            }
        """
        variables = {"collection_handle": collection_handle}
        res = self.run_query(query, variables)
        res = res["collectionByHandle"]["products"]["nodes"]
        assert (
            len(res) < 100
        ), f"Too many products found for {collection_handle}: {len(res)}"
        return res
