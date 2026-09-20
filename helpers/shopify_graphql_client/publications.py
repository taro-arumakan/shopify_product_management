import datetime
import logging
from helpers.exceptions import NoProductsFoundException

logger = logging.getLogger(__name__)

# The only channel whose publishDate Shopify honours - see
# publish_by_product_or_collection_id.
ONLINE_STORE = "Online Store"


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
        publication = self.publication_by_publication_name(ONLINE_STORE)
        if len(publication["products"]["nodes"]) == 250:
            raise RuntimeError(
                f"number of products included in the publicaiton may have exceeded the query limit. check the products."
            )
        return publication

    def publish_by_product_or_collection_id(
        self, product_or_collection_id, scheduled_time: datetime.datetime = None
    ):
        logger.info(
            f"Publishing {product_or_collection_id} {f'at {scheduled_time}' if scheduled_time else 'immediately'}"
        )
        publications = self.publications()
        params = {"product_or_collection_id": product_or_collection_id}
        skipped = []
        for publication in publications:
            params["publication_id"] = publication["id"]
            if scheduled_time and publication["name"] == ONLINE_STORE:
                self.publish_by_product_or_collection_id_and_publication_id(
                    scheduled_time=scheduled_time, **params
                )
            elif not scheduled_time:
                self.publish_by_product_or_collection_id_and_publication_id(**params)
            else:
                skipped.append(publication["name"])
        if skipped:
            # Shopify ignores publishDate outside the Online Store, so publishing
            # these now would put the product live ahead of the launch.
            logger.info(
                f"  not publishing to {', '.join(skipped)}: only the {ONLINE_STORE} "
                f"honours a publish date. Run helpers/publication_catch_up.py "
                f"after {scheduled_time} to publish them."
            )

    def activate_and_publish_by_product_id(
        self, product_id, scheduled_time: datetime.datetime = None
    ):
        """
        publish the product immediately or at a scheduled time, and activate it
        """
        product_id = self.sanitize_id(product_id)
        self.publish_by_product_or_collection_id(product_id, scheduled_time)
        self.update_product_status(product_id, "ACTIVE")

    def publish_by_product_or_collection_id_and_publication_id(
        self,
        product_or_collection_id,
        publication_id,
        scheduled_time: datetime.datetime = None,
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
        variables = {
            "id": product_or_collection_id,
            "input": {"publicationId": publication_id},
        }
        if scheduled_time:
            assert (
                scheduled_time.tzinfo
            ), f"scheduled_time must be timezone-aware: {scheduled_time}"
            variables["input"]["publishDate"] = scheduled_time.isoformat()
        res = self.run_query(query, variables)
        if user_errors := res["publishablePublish"]["userErrors"]:
            raise RuntimeError(f"Failed to publish product: {user_errors}")
        return res["publishablePublish"]["publishable"]

    def unpublish_by_product_or_collection_id_and_publication_id(
        self, product_or_collection_id, publication_id
    ):
        query = """
        mutation publishableUnpublish($id: ID!, $input: [PublicationInput!]!) {
            publishableUnpublish(id: $id, input: $input) {
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
        variables = {
            "id": product_or_collection_id,
            "input": {"publicationId": publication_id},
        }
        res = self.run_query(query, variables)
        if user_errors := res["publishableUnpublish"]["userErrors"]:
            raise RuntimeError(f"Failed to unpublish product: {user_errors}")
        return res["publishableUnpublish"]["publishable"]

    def unpublish_by_product_or_collection_id(
        self, product_or_collection_id, publication_names
    ):
        """Unpublish from the named publications.

        The names are required on purpose: unpublishing everything would take
        the Online Store down with the rest, and a scheduled Online Store
        publication is usually the one thing worth keeping.
        """
        publication_names = set(publication_names)
        logger.info(
            f"Unpublishing {product_or_collection_id} from "
            f"{', '.join(sorted(publication_names))}"
        )
        res = []
        for publication in self.publications():
            if publication["name"] in publication_names:
                res.append(
                    self.unpublish_by_product_or_collection_id_and_publication_id(
                        product_or_collection_id, publication["id"]
                    )
                )
                publication_names.discard(publication["name"])
        if publication_names:
            raise RuntimeError(
                f"no such publication(s): {', '.join(sorted(publication_names))}"
            )
        return res

    def product_publication_states(self, product_id):
        """Every sales channel this product could be on, with its publish state.

        `onlyPublished: false` also returns the channels it is not on, and a
        publication still waiting for its publishDate comes back with
        isPublished false and that date - which is how the catch-up tells a
        scheduled launch from one that has already happened.
        """
        query = """
        query productPublications($id: ID!) {
            product(id: $id) {
                id
                title
                resourcePublicationsV2(first: 50, onlyPublished: false) {
                    nodes {
                        isPublished
                        publishDate
                        publication {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        product_id = self.sanitize_id(product_id)
        res = self.run_query(query, {"id": product_id})
        if not (product := res.get("product")):
            raise NoProductsFoundException(f"No product found for {product_id}")
        return product["resourcePublicationsV2"]["nodes"]
