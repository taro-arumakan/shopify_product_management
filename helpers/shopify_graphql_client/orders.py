import datetime
import logging
import zoneinfo

logger = logging.getLogger(__name__)


class Orders:
    def orders_by_query(
        self,
        query_string,
        additional_fields=None,
        sort_key="PROCESSED_AT",
        reverse=False,
    ):
        reverse = "true" if reverse else "false"
        query = """
        query ordersByQuery($query_string: String!) {
            orders(first: 200, query: $query_string, sortKey: %s, reverse: %s) {
                nodes {
                    id
                    name
                    displayFinancialStatus
                    createdAt
                    processedAt%s
                    customer {
                        id
                        displayName
                        defaultEmailAddress {
                            emailAddress
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
        return res["orders"]["nodes"]

    def orders_by_sku(
        self,
        sku,
        created_after_date: datetime.datetime = None,
        open_only: bool = False,
    ):
        query_string = f"sku:'{sku}'"
        if created_after_date:
            if isinstance(created_after_date, datetime.date):
                logger.warning(
                    "Querying without timezone in consideration. 'created_at' stored in Shopify are in UTC"
                )
            elif not created_after_date.tzinfo:
                created_after_date = created_after_date.astimezone(
                    zoneinfo.ZonInfo("Asia/Tokyo")
                ).astimezone(zoneinfo.ZoneInfo("UTC"))
            query_string += f" AND created_at:>={created_after_date:%Y-%m-%d}"
        if open_only:
            query_string += " AND status:'open' AND NOT financial_status:'expired'"
        return self.orders_by_query(query_string)

    def orders_later_than(self, cutoff_datetime: datetime.datetime):
        if not cutoff_datetime.tzinfo:
            logger.warning("converting parameter to Asia/Tokyo")
            cutoff_datetime = cutoff_datetime.replace(
                tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
            )
        return self.orders_by_query(f"created_at:>='{cutoff_datetime.isoformat()}'")
