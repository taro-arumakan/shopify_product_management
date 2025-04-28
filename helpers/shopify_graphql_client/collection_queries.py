import logging
class CollectionQueries:
    logger = logging.getLogger(f"{__module__}.{__qualname__}")
    def products_by_collection_id(self, collection_id):
        query = '''
        query ProductsByCollection ($id: ID!) {
            collection(id: $id) {
                handle
                products(first: 50) {
                nodes {
                    title,
                    id,
                    status
                }
                }
            }
        }
        '''
        variables = {
            'id': collection_id
        }
        res = self.run_query(query, variables)
        return res['collection']['products']['nodes']

    def collection_by_title(self, title):
        query = '''
        query collections {
            collections(first: 50, query: "title:'%s'") {
                nodes {
                    id
                    handle
                    title
                    sortOrder
                    templateSuffix
                    products(first:100) {
                        nodes {
                            id
                            title
                        }
                    }
                }
            }
        }''' % title
        res = self.run_query(query)
        if len(res['collections']['nodes']) != 1:
            raise RuntimeError(f"{'Multiple' if res['nodes'] else 'No'} collections found for {title}: {res['nodes']}")
        return res['collections']['nodes'][0]

    def collection_id_by_title(self, title):
        collection = self.collection_by_title(title)
        return collection['id']

    def collection_create(self, collection_title, product_ids):
        query = '''
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
        '''
        variables = {
            "input": {
                "title": collection_title,
                "products": [self.sanitize_id(product_id) for product_id in product_ids]
            }
        }
        res = self.run_query(query, variables)
        if errors := res['collectionCreate']['userErrors']:
            raise RuntimeError(f"Collection creation failed: {errors}")
        return res

    def collection_add_products(self, collection_id, product_ids):
        query = '''
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
        '''
        variables = {
            "id": collection_id,
            "productIds": [self.sanitize_id(product_id) for product_id in product_ids]
        }
        res = self.run_query(query, variables)
        if errors := res['collectionAddProducts']['userErrors']:
            raise RuntimeError(f"Failed to add products to the collection: {errors}")
        return res
