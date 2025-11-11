import logging

logger = logging.getLogger(__name__)


class CollectionQueries:

    def products_by_collection_id(self, collection_id):
        query = """
        query ProductsByCollection ($id: ID!) {
            collection(id: $id) {
                handle
                products(first: 50) {
                    nodes {
                        title,
                        id,
                        status
                        variants (first:10) {
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
                        }                    }
                }
            }
        }
        """
        variables = {"id": self.sanitize_id(collection_id, "Collection")}
        res = self.run_query(query, variables)
        return res["collection"]["products"]["nodes"]

    def collections_by_query(self, query_string):
        query = """
            query collections($query_string: String!) {
                collections(first: 200, query: $query_string) {
                    nodes {
                        id
                        handle
                        title
                        sortOrder
                        templateSuffix
                        products(first:200) {
                            nodes {
                                id
                                title
                            }
                        }
                    }
                }
            }
            """
        variables = {"query_string": query_string}
        res = self.run_query(query, variables)
        return res["collections"]["nodes"]

    def collection_by_title(self, title):
        res = self.collections_by_query(f"title:'{title}'")
        if len(res) != 1:
            raise RuntimeError(
                f"{'Multiple' if res else 'No'} collections found for {title}: {res}"
            )
        return res[0]

    def collections_by_title_prefix(self, title_prefix):
        return self.collections_by_query(f"title:{title_prefix}*")

    def collection_id_by_title(self, title):
        collection = self.collection_by_title(title)
        return collection["id"]

    def collection_create(self, collection_title, product_ids):
        query = """
        mutation createCollection($input: CollectionInput!) {
            collectionCreate(input: $input) {
                collection {
                    id
                    products(first: 30) {
                        nodes {
                            id
                            title
                        }
                    }
                }
                userErrors {
                    message
                    field
                }
            }
        }
        """
        variables = {
            "input": {
                "title": collection_title,
                "products": [
                    self.sanitize_id(product_id) for product_id in product_ids
                ],
            }
        }
        res = self.run_query(query, variables)
        if errors := res["collectionCreate"]["userErrors"]:
            raise RuntimeError(f"Collection creation failed: {errors}")
        return res

    def collection_add_products(self, collection_id, product_ids):
        query = """
        mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
            collectionAddProducts(id: $id, productIds: $productIds) {
                collection {
                    id
                    title
                    products(first: 10) {
                        nodes {
                            id
                            title
                        }
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
            "id": self.sanitize_id(collection_id, prefix="Collection"),
            "productIds": [self.sanitize_id(product_id) for product_id in product_ids],
        }
        res = self.run_query(query, variables)
        if errors := res["collectionAddProducts"]["userErrors"]:
            raise RuntimeError(f"Failed to add products to the collection: {errors}")
        return res
