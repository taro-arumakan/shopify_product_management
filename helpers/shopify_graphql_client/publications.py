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
                }
            }
        }
        """
        res = self.run_query(query)
        return res["publications"]["nodes"]

    def activate_and_publish_by_product_id(
        self, product_id, scheduled_time: datetime.datetime = None
    ):
        """
        publish the product immediately or at a scheduled time, and activate it
        """
        logger.info(
            f"Publishing product {product_id} {'at {scheduled_time}' if scheduled_time else 'immediately'}"
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
