import calendar
import datetime
import logging
import shutil

logger = logging.getLogger(__name__)

import pandas as pd


class Analytics:
    def run_shopifyql(self, shpoifyql_query, to_dataframe=True):
        query = (
            """
        query {
            shopifyqlQuery(query: "%s") {
                tableData {
                    columns {
                        name
                        dataType
                        displayName
                    }
                    rows
                }
                parseErrors
            }
        }
        """
            % shpoifyql_query
        )
        res = self.run_query(query)
        if error := res["shopifyqlQuery"]["parseErrors"]:
            raise RuntimeError(f"Failed to run ShpifyQL query: {error}")
        res = res["shopifyqlQuery"]["tableData"]
        return self.report_to_dataframe(res) if to_dataframe else res

    def report_to_dataframe(self, shopifyql_res):
        df = pd.DataFrame(shopifyql_res["rows"])
        df = df[[c["name"] for c in shopifyql_res["columns"]]]
        money_cols = [
            c["name"] for c in shopifyql_res["columns"] if c["dataType"] == "MONEY"
        ]
        date_cols = [
            c["name"]
            for c in shopifyql_res["columns"]
            if c["dataType"] == "DAY_TIMESTAMP"
        ]
        df[money_cols] = df[money_cols].apply(pd.to_numeric, errors="coerce")
        df[date_cols] = df[date_cols].apply(pd.to_datetime, errors="coerce")
        return df

    def report_sales_by_sku(self, date_from, date_to, to_dataframe=True):
        shopifyql_query = f"""
            FROM sales
            SHOW day, order_name, sale_id, discount_code, line_type, product_title_at_time_of_sale
                AS TITLE, product_variant_sku_at_time_of_sale AS SKU,
                product_variant_compare_at_price AS ORIGINAL_PRICE, product_variant_price AS SELLING_PRICE,
                gross_sales, net_returns, discounts,
                net_sales, shipping_charges, shipping_returned
            GROUP BY day, order_name, sale_id, discount_code, line_type, TITLE, SKU, ORIGINAL_PRICE, SELLING_PRICE
            TIMESERIES day
            SINCE {date_from:%Y-%m-%d} UNTIL {date_to:%Y-%m-%d}
            ORDER BY day ASC, order_name ASC, line_type ASC, SKU ASC
        """
        return self.run_shopifyql(shopifyql_query, to_dataframe=to_dataframe)

    def report_monthly_sales_by_sku(self, report_year, report_month, to_dataframe=True):
        return self.report_sales_by_sku(
            date_from=datetime.date(report_year, report_month, 1),
            date_to=datetime.date(
                report_year,
                report_month,
                calendar.monthrange(report_year, report_month)[1],
            ),
            to_dataframe=to_dataframe,
        )

    def inject_dataframe_to_xlsx(
        self, output_path, sheet_name, dataframe, startrow, header=False
    ):
        """
        Inject the dataframe to an xlsx file at output_path, at the specified startrow

        :param output_path: where the xlsx file is
        :param sheet_name: sheet name to insert the DataFrame to
        :param dataframe: DataFrame being injected
        :param startrow: 0 based row index
        :param header: whether to include header or not
        """
        # 'overlay' mode, 'a' stands for append
        with pd.ExcelWriter(
            output_path, engine="openpyxl", mode="a", if_sheet_exists="overlay"
        ) as writer:
            dataframe.to_excel(
                writer,
                sheet_name=sheet_name,
                startrow=startrow,
                index=False,
                header=header,
            )

    def generate_monthly_report(
        self, template_path, sheet_name, output_path, report_year, report_month
    ):
        shutil.copyfile(template_path, output_path)
        df = self.report_monthly_sales_by_sku(report_year, report_month)
        self.inject_dataframe_to_xlsx(
            output_path=output_path,
            sheet_name=sheet_name,
            dataframe=df,
            startrow=20,
            header=False,
        )
