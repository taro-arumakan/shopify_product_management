import datetime
import logging
import pathlib

logging.basicConfig(level=logging.INFO)

import utils


def run(brand, report_year, report_month):
    base_dir = pathlib.Path(__file__).resolve().parent
    template_path = f"{base_dir}/monthly_report_template.xlsx"
    client = utils.client(brand)
    output_path = f"/tmp/monthly_report_{datetime.date(report_year, report_month, 1):%Y%m}_{client.VENDOR}.xlsx"
    client.generate_monthly_report(
        template_path,
        sheet_name="monthly_sales_report",
        output_path=output_path,
        report_year=report_year,
        report_month=report_month,
    )
    target_folder_id = client.find_or_create_folder_by_name(
        parent_folder_id="1bGXNkunwH99lA9Usl8dYWJJ7yoO53bun",
        folder_name=f"{datetime.date(report_year, report_month, 1):%Y%m}",
    )
    client.upload_to_drive(
        filepath=output_path,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        folder_id=target_folder_id,
    )


def main():
    rundate = datetime.date.today()
    report_date = rundate.replace(day=1) - datetime.timedelta(days=1)
    brands = ["apricot", "blossom", "archive", "gbh", "kume", "lememe", "roh", "ssil"]
    for brand in brands:
        run(brand, report_date.year, report_date.month)


def adhoc():
    year_months = [(2025, 11), (2025, 12)]
    brands = ["apricot", "blossom", "archive", "gbh", "kume", "lememe", "roh", "ssil"]
    for brand in brands:
        for year, month in year_months:
            run(brand, year, month)


if __name__ == "__main__":
    # adhoc()
    main()
