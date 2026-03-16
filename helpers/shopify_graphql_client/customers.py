import datetime
import logging
import zoneinfo

logger = logging.getLogger(__name__)


class Customers:
    def customers_by_query(
        self,
        query_string,
        sort_key="NAME",
    ):
        query = """
        query customersByQuery($query_string: String!) {
            customers(first: 200, query: $query_string, sortKey: %s) {
                nodes {
                    id
                    firstName
                    lastName
                    defaultEmailAddress {
                        emailAddress
                        marketingState
                    }
                    tags
                }
            }
        }
        """ % (
            sort_key
        )
        variables = {"query_string": query_string}
        res = self.run_query(query, variables)
        return res["customers"]["nodes"]

    def customers_by_last_abandand_order_date(
        self,
        last_abandand_order_after: datetime.datetime,
    ):
        if isinstance(last_abandand_order_after, datetime.date):
            logger.warning(
                "Querying without timezone in consideration. 'last_abandand_order_date' stored in Shopify are in UTC"
            )
        elif not last_abandand_order_after.tzinfo:
            last_abandand_order_after = last_abandand_order_after.astimezone(
                zoneinfo.ZoneInfo("Asia/Tokyo")
            ).astimezone(zoneinfo.ZoneInfo("UTC"))
        query_string = (
            f"last_abandoned_order_date:>={last_abandand_order_after:%Y-%m-%d}"
        )
        return self.customers_by_query(query_string)

    def update_customers_tags(self, customer_id, tags):
        query = """
        mutation customerUpdate($input: CustomerInput!) {
            customerUpdate(input: $input) {
                customer {
                    id
                    tags
                    firstName
                    lastName
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
                "id": self.sanitize_id(customer_id, prefix="Customer"),
                "tags": tags,
            }
        }
        res = self.run_query(query, variables)
        if errors := res["customerUpdate"]["userErrors"]:
            raise RuntimeError(f"Failed to update tags: {errors}")
        return res["customerUpdate"]["customer"]
