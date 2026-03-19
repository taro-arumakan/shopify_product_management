import datetime
import logging

logging.basicConfig(level=logging.INFO)

import utils


def run(brand, report_year, report_month):
    client = utils.client(brand)
    output_path = f"/tmp/customer_type_donut{datetime.date(report_year, report_month, 1):%Y%m}_{client.VENDOR}.png"
    client.generate_monthly_store_kpi_graph(
        output_path=output_path,
        report_year=report_year,
        report_month=report_month,
    )
    target_folder_id = client.find_or_create_folder_by_name(
        parent_folder_id="1U-ZKzMcQrnaaD7W-2xsqY4e7bGWgmjDg",
        folder_name=f"{datetime.date(report_year, report_month, 1):%Y%m}",
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
