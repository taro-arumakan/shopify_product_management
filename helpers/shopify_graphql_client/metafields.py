import json
import logging

logger = logging.getLogger(__name__)


class Metafields:
    """
    This class provides methods to manage metafields in Shopify using GraphQL. Inherited by the ShopifyGraphqlClient class.
    """

    def update_product_metafield(
        self, product_id, metafield_namespace, metafield_key, value
    ):
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
                        "value": value,
                    }
                ],
            }
        }
        res = self.run_query(query, variables)
        if res["productUpdate"]["userErrors"]:
            raise RuntimeError(
                f"Error updating {metafield_namespace}.{metafield_key}: {res['productUpdate']['userErrors']}"
            )
        return res

    def update_variation_value_metafield(self, product_id, variation_value):
        return self.update_product_metafield(
            product_id, "custom", "variation_value", variation_value
        )

    def update_variation_products_metafield(self, product_id, variation_product_ids):
        return self.update_product_metafield(
            product_id,
            "custom",
            "variation_products",
            json.dumps(variation_product_ids),
        )

    def update_product_description_metafield(self, product_id, desc):
        return self.update_product_metafield(
            product_id, "custom", "product_description", json.dumps(desc)
        )

    def update_product_care_metafield(self, product_id, product_care):
        return self.update_product_metafield(
            product_id, "custom", "product_care", json.dumps(product_care)
        )

    def update_size_table_html_metafield(self, product_id, html_text):
        return self.update_product_metafield(
            product_id, "custom", "size_table_html", html_text
        )

    def update_product_number_metafield(self, product_id, product_number):
        return self.update_product_metafield(
            product_id, "custom", "product_number", product_number
        )

    def update_size_table_html_ja_metafield(self, product_id, html_text):
        return self.update_product_metafield(
            product_id, "custom", "size_table_html_ja", html_text
        )

    def update_size_table_html_en_metafield(self, product_id, html_text):
        return self.update_product_metafield(
            product_id, "custom", "size_table_html_en", html_text
        )

    def update_badges_metafield(self, product_id, badges: list[str]):
        return self.update_product_metafield(
            product_id, "custom", "badges", json.dumps(badges)
        )

    def update_discount_rate_metafield(self, product_id, discount_rate):
        return self.update_product_metafield(
            product_id, "custom", "discount_rate", discount_rate
        )

    def update_product_care_page_metafield(self, product_id, product_care_page_title):
        page_id = self.page_id_by_title(product_care_page_title)
        return self.update_product_metafield(
            product_id, "custom", "product_care_page", page_id
        )

    def metafield_id_by_namespace_and_key(self, namespace, key, owner_type="PRODUCT"):
        query = """
        query {
            metafieldDefinitions(first:10, ownerType:%s, namespace:"%s", key:"%s") {
                nodes {
                    id
                }
            }
        }
        """ % (
            owner_type,
            namespace,
            key,
        )
        res = self.run_query(query)
        res = res["metafieldDefinitions"]["nodes"]
        assert (
            len(res) == 1
        ), f'{"Multiple" if res else "No"} metafields found for {namespace}:{key}: {res}'
        return res[0]["id"]

    def product_metafield_value_by_product_id(
        self, product_id, namespace="custom", key="product_description"
    ):
        query = """
        query ProductMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
            product(id: $ownerId) {
                metafieldValue: metafield(namespace: $namespace, key: $key) {
                    value
                }
            }
        }
        """
        variables = {"ownerId": product_id, "namespace": namespace, "key": key}
        res = self.run_query(query, variables)
        return res["product"]["metafieldValue"]["value"]

    def convert_rich_text_to_html(self, json_value):
        def render_node(node):
            node_type = node.get("type")
            if node_type == "root":
                return "".join(render_node(child) for child in node.get("children", []))
            elif node_type == "paragraph":
                content = "".join(
                    render_node(child) for child in node.get("children", [])
                )
                return f"<p>{content}</p>"
            elif node_type == "heading":
                level = node.get("level", 1)
                content = "".join(
                    render_node(child) for child in node.get("children", [])
                )
                return f"<h{level}>{content}</h{level}>"
            elif node_type == "text":
                return node.get("value", "")
            else:
                raise RuntimeError(f"unhandled node type: {node_type}")

        parsed = json.loads(json_value)
        return render_node(parsed)
