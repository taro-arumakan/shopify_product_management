import collections
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

    def remove_punctuations(self, s):
        parts = s.lower().split(" ")
        parts = [part.translate(punctuation_translator) for part in parts]
        return "-".join(parts)

    def product_title_to_handle(self, title, handle_suffix=None):
        if handle_suffix:
            title += f" {handle_suffix}"
        return self.remove_punctuations(title)

    def products_by_query(
        self,
        query_string,
        additional_fields=None,
        sort_key="TITLE",
        reverse=False,
        raise_if_too_many=True,
    ):
        reverse = "true" if reverse else "false"
        query = """
        query productsByQuery($query_string: String!) {
            products(first: 200, query: $query_string, sortKey: %s, reverse: %s) {
                nodes {
                    id
                    title
                    handle
                    status
                    tags%s
                    metafields (first:10) {
                        nodes {
                            id
                            namespace
                            key
                            value
                        }
                    }
                    variants (first:30) {
                        nodes {
                            id
                            title
                            sku
                            price
                            compareAtPrice
                            inventoryQuantity
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
                            ... on MediaImage {
                                id
                                image {
                                    id
                                    url
                                }
                            }
                        }
                    }
                }
            }
        }
        """ % (
            sort_key,
            reverse,
            f"\n{'\n'.join(additional_fields)}" if additional_fields else "",
        )
        variables = {"query_string": query_string}
        res = self.run_query(query, variables)
        res = res["products"]["nodes"]
        if raise_if_too_many:
            assert (
                len(res) < 200
            ), f"Too many products found for {query_string}: {len(res)}"
        return res

    def products_by_title(self, title, *args, **kwargs):
        products = self.products_by_query(
            f"title:'{title.replace("'", "\\'")}'", *args, **kwargs
        )
        if len(products) == 0:
            raise NoProductsFoundException(f"No products found for {title}")
        return products

    def product_ids_by_title(self, title):
        res = self.products_by_title(title)
        return [r["id"] for r in res]

    def products_by_tag(self, tag, *args, **kwargs):
        return self.products_by_query(f"tag:'{tag}'", *args, **kwargs)

    def products_by_metafield(
        self, metafield_namespace, metafield_key, metafield_value, *args, **kwargs
    ):
        if type(metafield_value) is str:
            metafield_value = f'"{metafield_value}"'
        return self.products_by_query(
            f"metafields.{metafield_namespace}.{metafield_key}:{metafield_value}",
            *args,
            **kwargs,
        )

    def product_by_query(self, query_string, *args, **kwargs):
        products = self.products_by_query(query_string, *args, **kwargs)
        if len(products) != 1:
            products = [p for p in products if p["status"] != "ARCHIVED"]
            if len(products) != 1:
                raise (
                    MultipleProductsFoundException
                    if products
                    else NoProductsFoundException
                )(
                    f"{'Multiple' if products else 'No'} products found for {query_string}: {products}"
                )
        return products[0]

    def product_by_id(self, identifier, *args, **kwargs):
        return self.products_by_query(
            f"id:'{identifier.rsplit('/', 1)[-1]}'", *args, **kwargs
        )[0]

    def product_by_title(self, title, *args, **kwargs):
        return self.product_by_query(
            f"title:'{title.replace("'", "\\'")}'", *args, **kwargs
        )

    def product_id_by_title(self, title):
        return self.product_by_title(title)["id"]

    def product_by_handle(self, handle, *args, **kwargs):
        return self.product_by_query(f"handle:'{handle}'", *args, **kwargs)

    def product_id_by_handle(self, handle):
        return self.product_by_handle(handle)["id"]

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
        return self.product_variants_by_query(
            f"product_id:{product_id}", filter_archived=False
        )

    def product_variants_by_tag(self, tag, **kwargs):
        return self.product_variants_by_query(f"tag:'{tag}'", **kwargs)

    def variant_by_variant_id(self, variant_id):
        variant_id = self.sanitize_id(variant_id, "ProductVariant").rsplit("/", 1)[-1]
        if (
            len(
                res := self.product_variants_by_query(
                    f"id:{variant_id}", filter_archived=False
                )
            )
            != 1
        ):
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

    def product_titles_with_multiple_products(self):
        """
        Product titles with multiple products i.e. merge candidates.
        Titles are returned in lower.
        """
        products = self.products_by_query("status:'ACTIVE'")
        counts_by_title = collections.Counter(p["title"].lower() for p in products)
        return [title for title, count in counts_by_title.items() if count > 1]
