import calendar
import datetime
import logging
import shutil

logger = logging.getLogger(__name__)

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec


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
        return self.tabledata_to_dataframe(res) if to_dataframe else res

    def tabledata_to_dataframe(self, shopifyql_res):
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

    def report_total_sales_by_product(self, date_from, date_to, to_dataframe=True):
        shopifyql_query = f"""
            FROM sales
            SHOW total_sales
            WHERE product_title IS NOT NULL
            GROUP BY product_title, product_vendor, product_type WITH TOTALS, CURRENCY 'JPY'
            SINCE {date_from:%Y-%m-%d} UNTIL {date_to:%Y-%m-%d}
            ORDER BY total_sales DESC
        """
        return self.run_shopifyql(shopifyql_query, to_dataframe=to_dataframe)

    def report_total_sales(self, date_from, date_to, to_dataframe=True):
        shopifyql_query = f"""
            FROM sales
            SHOW total_sales
            TIMESERIES day WITH TOTALS, CURRENCY 'JPY'
            SINCE {date_from:%Y-%m-%d} UNTIL {date_to:%Y-%m-%d}
            ORDER BY day ASC
        """
        return self.run_shopifyql(shopifyql_query, to_dataframe=to_dataframe)

    def report_average_order_value(self, date_from, date_to, to_dataframe=True):
        shopifyql_query = f"""
            FROM sales
            SHOW orders, average_order_value
            WHERE excludes_post_order_adjustments = true
            TIMESERIES day WITH TOTALS, CURRENCY 'JPY'
            SINCE {date_from:%Y-%m-%d} UNTIL {date_to:%Y-%m-%d}
            ORDER BY day ASC
        """
        return self.run_shopifyql(shopifyql_query, to_dataframe=to_dataframe)

    def report_sessions(self, date_from, date_to, to_dataframe=True):
        shopifyql_query = f"""
            FROM sessions
            SHOW sessions, conversion_rate
            TIMESERIES day WITH TOTALS, CURRENCY 'JPY'
            SINCE {date_from:%Y-%m-%d} UNTIL {date_to:%Y-%m-%d}
            ORDER BY day ASC
        """
        return self.run_shopifyql(shopifyql_query, to_dataframe=to_dataframe)

    def run_monthly_report(
        self, report_func, report_year, report_month, to_dataframe=True
    ):
        return report_func(
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

    def generate_monthly_sales_report(
        self, template_path, sheet_name, output_path, report_year, report_month
    ):
        shutil.copyfile(template_path, output_path)
        df = self.run_monthly_report(
            self.report_sales_by_sku, report_year, report_month
        )
        self.inject_dataframe_to_xlsx(
            output_path=output_path,
            sheet_name=sheet_name,
            dataframe=df,
            startrow=20,
            header=False,
        )

    def generate_monthly_sales_by_product_graph(
        self, output_path, report_year, report_month
    ):
        df = self.run_monthly_report(
            self.report_total_sales_by_product, report_year, report_month
        )
        df = df[["product_title", "total_sales"]].sort_values(
            by="total_sales", ascending=False
        )

        top_8 = df.head(8).copy()  # 2. Group Top 8 + Others
        others_val = df.iloc[8:]["total_sales"].sum()
        others_df = pd.DataFrame(
            [{"product_title": "Others", "total_sales": others_val}]
        )
        plot_df = pd.concat([top_8, others_df], ignore_index=True)

        # indices: 0:Blue, 1:Orange, 2:Green, 3:Red, 4:Purple, 5:Brown, 6:Pink, 7:Gray, 9:Cyan (for Others)
        tab10 = plt.get_cmap("tab10").colors
        custom_colors = list(tab10[:8]) + [tab10[9]]

        fig, ax = plt.subplots(figsize=(12, 10))

        wedges, texts, autotexts = ax.pie(
            plot_df["total_sales"],
            labels=plot_df["product_title"],
            autopct="%1.1f%%",
            startangle=90,  # Start at top center
            counterclock=False,  # Go clockwise
            colors=custom_colors,
            pctdistance=0.75,  # Position percentages inside the slices
            labeldistance=1.05,  # Position labels just outside
            wedgeprops={
                "linewidth": 1.5,
                "edgecolor": "white",
                "width": 1,  # Thick donut: covers full area towards center
            },
            textprops={"fontsize": 9},
        )

        for autotext in autotexts:  # 5. Fine-tune Text Styling
            autotext.set_fontsize(8)
            autotext.set_weight("bold")
            autotext.set_color("black")

        for text in texts:
            text.set_fontsize(8)

        plt.title(
            "Product Sales Share — Top Products + Others",
            fontsize=16,
            pad=30,
            fontweight="bold",
        )
        ax.axis("equal")

        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close(fig)

    def generate_monthly_store_kpi_graph(self, output_path, report_year, report_month):

        df_total_sales = self.run_monthly_report(
            self.report_total_sales, report_year, report_month
        )
        df_aov = self.run_monthly_report(
            self.report_average_order_value, report_year, report_month
        )
        df_cvr = self.run_monthly_report(
            self.report_sessions, report_year, report_month
        )

        def clean_numeric(series):
            return pd.to_numeric(
                series.astype(str).str.replace(",", ""), errors="coerce"
            ).fillna(0)

        df_total_sales["total_sales"] = clean_numeric(df_total_sales["total_sales"])
        df_aov["orders"] = clean_numeric(df_aov["orders"]).astype(int)
        df_aov["average_order_value"] = clean_numeric(df_aov["average_order_value"])
        df_cvr["sessions"] = clean_numeric(df_cvr["sessions"]).astype(int)
        df_cvr["conversion_rate"] = clean_numeric(df_cvr["conversion_rate"])

        df = pd.merge(df_aov, df_cvr, on="day", how="outer").sort_values("day")
        df = pd.merge(df, df_total_sales, on="day", how="outer").sort_values("day")
        df["day"] = pd.to_datetime(df["day"])

        # 2. KPI Calculations (for the left panel)
        total_sales = df["total_sales"].sum()
        total_sessions = df["sessions"].sum()
        avg_cvr = float(df["conversion_rate__totals"][0]) * 100
        avg_aov = int(df["average_order_value__totals"][0])

        # 3. Setup Layout (Left: Summary, Right: Charts)
        fig = plt.figure(figsize=(14, 10), facecolor="white")
        gs = GridSpec(3, 2, width_ratios=[1, 3], figure=fig, hspace=0.4, wspace=0.1)

        # --- LEFT PANEL: Summary Text ---
        # We use a single axis for the whole left side to place text accurately
        ax_text = fig.add_subplot(gs[:, 0])
        ax_text.axis("off")

        kpis = [
            ("TOTAL SALES", f"¥{int(total_sales):,}", 0.85),
            ("TOTAL SESSIONS", f"{int(total_sessions):,}", 0.60),
            ("AVERAGE CVR", f"{avg_cvr:.2f}%", 0.35),
            ("AVERAGE AOV", f"¥{int(avg_aov):,}", 0.10),
        ]

        for label, val, y_pos in kpis:
            ax_text.text(
                0.1, y_pos + 0.05, label, fontsize=10, color="gray", fontweight="bold"
            )
            ax_text.text(0.1, y_pos, val, fontsize=24, fontweight="bold")
            ax_text.axhline(
                y_pos - 0.08, xmin=0.1, xmax=0.9, color="lightgray", linewidth=0.5
            )

        # --- RIGHT PANEL: Charts ---

        # Chart 1: Sales (Bars) & Sessions (Line) - Dual Axis
        ax1 = fig.add_subplot(gs[0, 1])
        ax1_twin = ax1.twinx()

        ax1.bar(df["day"], df["total_sales"], color="#4E91C2", alpha=0.8, label="Sales")
        ax1_twin.plot(
            df["day"],
            df["sessions"],
            color="#F39233",
            marker="o",
            markersize=3,
            label="sessions",
        )

        ax1.set_title("Sales & Sessions", fontsize=12, fontweight="bold", loc="left")
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{int(x):,}"))

        # Chart 2: Conversion Rate (Line)
        ax2 = fig.add_subplot(gs[1, 1])
        cvr_data = df["conversion_rate"] * 100
        ax2.plot(df["day"], cvr_data, color="#31A354", marker="o", markersize=3)
        ax2.axhline(
            cvr_data.mean(), color="#31A354", linestyle="--", alpha=0.4
        )  # Average line
        ax2.set_title("conversion_rate", fontsize=12, fontweight="bold", loc="left")
        ax2.set_ylabel("%")

        # Chart 3: Average Order Value (Line)
        ax3 = fig.add_subplot(gs[2, 1])
        ax3.plot(
            df["day"],
            df["average_order_value"],
            color="#D62728",
            marker="o",
            markersize=3,
        )
        ax3.axhline(
            df["average_order_value"].mean(), color="#D62728", linestyle="--", alpha=0.4
        )
        ax3.set_title("Average Order Value", fontsize=12, fontweight="bold", loc="left")
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{int(x):,}"))

        # Clean up formatting for all charts
        for ax in [ax1, ax2, ax3]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
            ax.tick_params(axis="both", labelsize=9)
            ax.grid(axis="y", linestyle="--", alpha=0.3)
            for spine in ["top", "right"]:
                ax.spines[spine].set_visible(False)

        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
