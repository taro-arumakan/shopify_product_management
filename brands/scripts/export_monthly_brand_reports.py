import datetime
import logging

logging.basicConfig(level=logging.INFO)

import utils


def update_graphs(brand_name, report_year, report_month):
    client = utils.client(brand_name)
    presentation_id = client.find_monthly_brand_report(
        brand_name, report_year, report_month
    )
    alt_text_file_id_map = {
        graph_name: client.get_graph_image_id(
            report_year=report_year,
            report_month=report_month,
            brand_name=brand_name,
            graph_name=graph_name,
        )
        for graph_name in ["store_kpi_by_day_graph"]
    }
    requests = client.populate_image_replacement_requests(
        presentation_id, alt_text_file_id_map
    )
    client.replace_slide_contents(presentation_id, requests)


def run(brand, report_year, report_month):
    graphs = [
        "store_kpi_graph",
        "sales_by_product_graph",
        "customer_type_donut",
        "conversion_breakdown",
    ]
    client = utils.client(brand)
    target_folder_id = client.find_or_create_folder_by_name(
        parent_folder_id=parent_folder_id,
        folder_name=f"{datetime.date(report_year, report_month, 1):%Y%m}",
    )
    for graph in graphs:
        logging.info(f"uploadging {graph} for {brand}")
        output_path = f"/tmp/{brand}_{graph}.png"
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
    logging.info(f"uploadging monthly report for {brand}")
    client.generate_monthly_brand_report(brand, report_year, report_month)


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
        run(brand, report_date.year, report_date.month)


def adhoc():
    year_months = [(2025, 11), (2025, 12), (2026, 1)]
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
    for year, month in year_months:
        for brand in brands:
            run(brand, year, month)


if __name__ == "__main__":
    # adhoc()
    main()
