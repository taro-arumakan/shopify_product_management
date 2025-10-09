import datetime
import logging

logger = logging.getLogger(__name__)


class Publications:
    def publications(self):
        query = """
        query publications{
            publications(first:100) {
                nodes {
                    id
                    name
                    catalog {
                        title
                        status
                    }
                    products(first:250) {
                        nodes {
                            id
                            title
                            variants(first:30) {
                                nodes {
                                    id
                                    title
                                    sku
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        res = self.run_query(query)
        return res["publications"]["nodes"]

    def publication_by_publication_name(self, name):
        publications = self.publications()
        for publication in publications:
            if publication["name"] == name:
                return publication

    def online_store_publication(self):
        publication = self.publication_by_publication_name("Online Store")
        if len(publication["products"]["nodes"]) == 250:
            raise RuntimeError(
                f"number of products included in the publicaiton may have exceeded the query limit. check the products."
            )
        return publication

    def activate_and_publish_by_product_id(
        self, product_id, scheduled_time: datetime.datetime = None
    ):
        """
        publish the product immediately or at a scheduled time, and activate it
        """
        logger.info(
            f"Publishing product {product_id} {f'at {scheduled_time}' if scheduled_time else 'immediately'}"
        )
        publications = self.publications()
        params = {"product_id": product_id}
        for publication in publications:
            params["publication_id"] = publication["id"]
            if scheduled_time and publication["name"] == "Online Store":
                self.publish_by_product_id_and_publication_id(
                    scheduled_time=scheduled_time, **params
                )
            else:
                self.publish_by_product_id_and_publication_id(**params)
        self.update_product_status(product_id, "ACTIVE")

    def publish_by_product_id_and_publication_id(
        self, product_id, publication_id, scheduled_time: datetime.datetime = None
    ):
        query = """
        mutation publishablePublish($id: ID!, $input: [PublicationInput!]!) {
            publishablePublish(id: $id, input: $input) {
                publishable {
                    ... on Product {
                        id
                        title
                    }
                    ... on Collection {
                        id
                        title
                    }
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """
        variables = {"id": product_id, "input": {"publicationId": publication_id}}
        if scheduled_time:
            assert (
                scheduled_time.tzinfo
            ), f"scheduled_time must be timezone-aware: {scheduled_time}"
            variables["input"]["publishDate"] = scheduled_time.isoformat()
        res = self.run_query(query, variables)
        if user_errors := res["publishablePublish"]["userErrors"]:
            raise RuntimeError(f"Failed to publish product: {user_errors}")
        return res["publishablePublish"]["publishable"]
