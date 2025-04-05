import json

class MetafieldsManagement:
    """
    This class provides methods to manage metafields in Shopify using GraphQL. Inherited by the ShopifyGraphqlClient class.
    """
    def update_product_metafield(self, product_id, metafield_namespace, metafield_key, value):
        query = """
        mutation updateProductMetafield($input: ProductInput!) {
            productUpdate(input: $input) {
                product {
                    id
                    metafields (first:10) {
                        nodes {
                            id
                            namespace
                            key
                            value
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
            "input": {
                "id": self.sanitize_id(product_id),
                "metafields": [
                    {
                        "namespace": metafield_namespace,
                        "key": metafield_key,
                        "value": value
                    }
                ]
            }
        }
        res = self.run_query(query, variables)
        return res

    def update_variation_value_metafield(self, product_id, variation_value):
        return self.update_product_metafield(product_id, 'custom', 'variation_value', variation_value)

    def update_variation_products_metafield(self, product_id, variation_product_ids):
        return self.update_product_metafield(product_id, 'custom', 'variation_products', json.dumps(variation_product_ids))

    def update_product_description_metafield(self, product_id, desc):
        return self.update_product_metafield(product_id, 'custom', 'product_description', json.dumps(desc))

    def update_size_table_html_metafield(self, product_id, html_text):
        return self.update_product_metafield(product_id, 'custom', 'size_table_html', html_text)

    def metafield_id_by_namespace_and_key(self, namespace, key, owner_type='PRODUCT'):
        query = '''
        query {
            metafieldDefinitions(first:10, ownerType:%s, namespace:"%s", key:"%s") {
                nodes {
                    id
                }
            }
        }
        ''' % (owner_type, namespace, key)
        res = self.run_query(query)
        res = res['metafieldDefinitions']['nodes']
        assert len(res) == 1, f'{"Multiple" if res else "No"} metafields found for {namespace}:{key}: {res}'
        return res[0]['id']
