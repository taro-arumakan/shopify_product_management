import datetime
import logging
import pathlib

logging.basicConfig(level=logging.INFO)

import utils


def run(brand, report_date: datetime.date):
    base_dir = pathlib.Path(__file__).resolve().parent
    template_path = f"{base_dir}/monthly_kpi_report_template.xlsx"
    client = utils.client(brand)
    output_path = f"/tmp/{report_date:%Y%m}_{brand}_monthly_kpi_report.xlsx"
    client.generate_kpi_by_month_report(
        template_path=template_path,
        sheet_name="Shopify KPI Monthly",
        output_path=output_path,
        date_from=datetime.date(2025, 10, 1),
        date_to=report_date,
    )
    target_folder_id = client.find_or_create_folder_by_name(
        parent_folder_id="1I6MA4aDfoAoiNgfxRx0GFRiGpSE7F380",
        folder_name=f"{report_date:%Y%m}",
    )
    client.upload_to_drive(
        filepath=output_path,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        folder_id=target_folder_id,
    )


def main():
    rundate = datetime.date.today()
    report_date = rundate.replace(day=1) - datetime.timedelta(days=1)
    brands = [
        "Apricot Studios",
        "BLOSSOM",
        "Archivépke",
        "GBH",
        "KUMÉ",
        "LEMEME",
        "ROH SEOUL",
        "SSIL",
    ]
    for brand in brands:
        run(brand, report_date)


if __name__ == "__main__":
    main()
