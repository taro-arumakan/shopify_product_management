import datetime
import logging

logging.basicConfig(level=logging.INFO)

import utils

parent_folder_id = "1qIl57QGB0TCgD_IsZ4vcFjxBbjZQVomN"


def run(brand, report_year, report_month):
    graphs = [
        "daily_store_kpi_graph",
        "sales_by_product_graph",
        "customer_type_donut",
        "conversion_breakdown",
    ]
    client = utils.client(brand)
    target_folder_id = client.find_or_create_folder_by_name(
        parent_folder_id=parent_folder_id,
        folder_name=f"{datetime.date(report_year, report_month, 1):%Y%m}",
    )
    for i, graph in enumerate(graphs):
        output_path = f"/tmp/{client.VENDOR}_{datetime.date(report_year, report_month, 1):%Y%m}_{str(i).zfill(2)}_{graph}_.png"
        client.generate_monthly(
            getattr(client, f"generate_{graph}"),
            output_path=output_path,
            report_year=report_year,
            report_month=report_month,
        )
        client.upload_to_drive(
            filepath=output_path,
            mimetype="image/png",
            folder_id=target_folder_id,
        )


def main():
    rundate = datetime.date.today()
    report_date = rundate.replace(day=1) - datetime.timedelta(days=1)
    brands = ["apricot", "blossom", "archive", "gbh", "kume", "lememe", "roh", "ssil"]
    for brand in brands:
        run(brand, report_date.year, report_date.month)


def adhoc():
    year_months = [(2025, 11), (2025, 12), (2026, 1)]
    brands = ["apricot", "blossom", "archive", "gbh", "kume", "lememe", "roh", "ssil"]
    for year, month in year_months:
        for brand in brands:
            run(brand, year, month)


if __name__ == "__main__":
    adhoc()
    main()
