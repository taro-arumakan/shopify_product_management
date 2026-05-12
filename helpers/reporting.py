import datetime
import logging
import pandas as pd
import pprint

logger = logging.getLogger(__name__)


class Reporting:

    SLIDES_TEMPLATE_ID = "1jhxdJvbCrF3dozSi819lbkAKt9N45zqjfeNvAddsCxI"
    LOGO_FOLDER_ID = "1tGmwEe0dJrWuVHtnUqnxU3bxbIO0JJoB"
    MONTHLY_IMAGES_FOLDER_ID = "13e7ejhsYGaelUwwteM3SC6_aMrhEsZW4"
    MONTHLY_REPORT_OUTPUT_FOLDER_ID = "1WCmMFHnFBnSin439p1OGFEyQdgDr9lNh"

    monthly_report_graph_names = [
        "store_kpi_by_day_graph",
        "sales_by_product_graph",
        "customer_type_donut",
        "conversion_breakdown",
    ]

    def get_logo_image_id(self, brand_name):
        res = self.find_by_folder_id_by_name(
            self.LOGO_FOLDER_ID, f"logo_{brand_name}.png"
        )
        return res["id"]

    def get_graph_image_id(self, report_year, report_month, brand_name, graph_name):
        parent_folder_id = self.find_folder_id_by_name(
            self.MONTHLY_IMAGES_FOLDER_ID,
            f"{str(report_year).zfill(2)}{str(report_month).zfill(2)}",
        )
        res = self.find_by_folder_id_by_name(
            parent_folder_id, f"{brand_name}_{graph_name}.png"
        )
        return res["id"]

    def generate_monthly_brand_report_graphs(
        self, brand_name, report_year, report_month
    ):
        graph_target_folder_id = self.find_or_create_folder_by_name(
            parent_folder_id=self.MONTHLY_IMAGES_FOLDER_ID,
            folder_name=f"{datetime.date(report_year, report_month, 1):%Y%m}",
        )
        for graph in self.monthly_report_graph_names:
            logger.info(
                f"{self.__class__.__name__} - uploadging {graph} to {graph_target_folder_id}"
            )
            output_path = f"/tmp/{brand_name}_{graph}.png"
            self.generate_monthly(
                getattr(self, f"generate_{graph}"),
                output_path=output_path,
                report_year=report_year,
                report_month=report_month,
            )
            self.upload_to_drive(
                filepath=output_path,
                mimetype="image/png",
                folder_id=graph_target_folder_id,
            )

    def find_monthly_brand_report(self, brand_name, report_year, report_month):
        return self.find_or_create_monthly_brand_report(
            brand_name, report_year, report_month, create=False
        )

    def find_or_create_monthly_brand_report(
        self, brand_name, report_year, report_month, create=True
    ):
        destination_folder_id = self.find_or_create_folder_by_name(
            self.MONTHLY_REPORT_OUTPUT_FOLDER_ID,
            f"{str(report_year).zfill(2)}{str(report_month).zfill(2)}",
        )
        title = f"[{brand_name}] {report_year}.{report_month} Review and Strategic Recommendations"
        if p := self.find_by_folder_id_by_name(destination_folder_id, title):
            presentation_id = p["id"]
            logger.info(
                f"{self.__class__.__name__} found an existing presentation {presentation_id}"
            )
        elif not create:
            raise RuntimeError(f"slide not found in {destination_folder_id}: {title}")
        else:
            body = {
                "name": title,
                "parents": [destination_folder_id],
                "supportsAllDrives": True,
            }
            logger.info(
                f"{self.__class__.__name__} copying template to {destination_folder_id}/{title}"
            )
            new_presentation = (
                self.drive_service.files()
                .copy(
                    fileId=self.SLIDES_TEMPLATE_ID,
                    body=body,
                    supportsAllDrives=True,
                )
                .execute()
            )
            presentation_id = new_presentation.get("id")
            logger.info(f"{self.__class__.__name__} copied to {presentation_id}")
        return presentation_id

    def populate_image_replacement_requests(
        self, presentation_id, alt_text_file_id_map
    ):
        presentation = (
            self.slides_service.presentations()
            .get(presentationId=presentation_id)
            .execute()
        )
        res = []
        for slide in presentation.get("slides", []):
            for element in slide.get("pageElements", []):
                alt_text = element.get("description", "")
                if alt_text in alt_text_file_id_map:
                    res.append(
                        {
                            "replaceImage": {
                                "imageObjectId": element["objectId"],
                                "imageReplaceMethod": "CENTER_INSIDE",
                                "url": self.get_direct_url(
                                    alt_text_file_id_map[alt_text]
                                ),
                            }
                        }
                    )
                    res.append(
                        {
                            "updatePageElementAltText": {
                                "objectId": element["objectId"],
                                "title": element.get("title", ""),
                                "description": alt_text,
                            }
                        }
                    )
        return res

    def replace_slide_contents(self, presentation_id, requests):
        logger.info(f"{self.__class__.__name__} replacing contents")
        image_urls = [r["replaceImage"]["url"] for r in requests if "replaceImage" in r]
        image_file_ids = [direct_url.rsplit("&id=", 1)[-1] for direct_url in image_urls]
        try:
            logger.debug(
                f"{self.__class__.__name__} making files public temporarily:\n{'\n'.join(image_urls)}"
            )
            for file_id in image_file_ids:
                self.make_public_by_file_id(file_id)

            logger.debug(
                f"{self.__class__.__name__} replacing contents:\n{pprint.pformat(requests, indent=2, width=80)}"
            )
            self.slides_service.presentations().batchUpdate(
                presentationId=presentation_id, body={"requests": requests}
            ).execute()

        finally:
            logger.info(f"{self.__class__.__name__} making files private")
            for file_id in image_file_ids:
                self.make_private_by_file_id(file_id)

    def generate_monthly_brand_report(self, brand_name, report_year, report_month):
        logger.info(f"{self.__class__.__name__} generating graphs")
        self.generate_monthly_brand_report_graphs(brand_name, report_year, report_month)
        presentation_id = self.find_or_create_monthly_brand_report(
            brand_name, report_year, report_month
        )

        # Define Replacements
        # Note: Slides API requires publicly accessible image URLs.
        requests = [
            {
                "replaceAllText": {
                    "replaceText": f"{report_year}.{report_month}",
                    "containsText": {"text": "{{YEARDATE}}"},
                }
            },
            {
                "replaceAllText": {
                    "replaceText": brand_name,
                    "containsText": {"text": "{{BRAND_NAME}}"},
                }
            },
        ]

        alt_text_file_id_map = {
            graph_name: self.get_graph_image_id(
                report_year=report_year,
                report_month=report_month,
                brand_name=brand_name,
                graph_name=graph_name,
            )
            for graph_name in self.monthly_report_graph_names
        }
        alt_text_file_id_map.update(brand_logo=self.get_logo_image_id(brand_name))

        image_replacement_requests = self.populate_image_replacement_requests(
            presentation_id, alt_text_file_id_map
        )
        requests += image_replacement_requests

        self.replace_slide_contents(presentation_id, requests)

    def dashboard_row(self, report_date, timeseries_by="month"):
        meta_stats = self.dashboard_stats_meta(report_date, timeseries_by)
        shopify_stats = self.dashboard_stats_shopify(report_date, timeseries_by)
        df = pd.merge(
            meta_stats,
            shopify_stats,
            left_on="report_date",
            right_on=timeseries_by,
            how="outer",
        )
        assert (
            len(df) == 1
        ), "Should not get multiple rows for a dashboard stats row:\ndf"
        row = df.iloc[0]
        return [
            f"{report_date:%Y-%m-%d}",
            self.BRAND_NAME,
            int(row["reach_omni"]),
            int(row["reach_paid"]) if row["reach_paid"] else "",
            int(row["profile_views_omni"]),
            int(row["profile_views_paid"]) if row["profile_views_paid"] else "",
            int(row["saves"]),
            int(row["sessions"]),
            # TODO should return the percentage as a float in tabledata_to_dataframe and delegate the formatting to presentation layer
            float(row["conversion_rate"]) / 100,
            int(row["average_order_value"]),
            int(row["net_sales"]),
            int(row["spend"]) if row["spend"] else "",
        ]

    def find_existing_row_index(self, worksheet, report_date, brand):
        # Find the row index (1-based for Google Sheets) matching with col date A and brand B
        all_values = worksheet.get_all_values()
        for i, existing_row in enumerate(all_values):
            if len(existing_row) >= 2:
                if existing_row[0] == report_date and existing_row[1] == brand:
                    return i + 1

    def upsert_dashboard_row(self, report_date, timeseries_by):
        # TODO if existing row with the date and brand, update, or delete then insert.
        sheet_name = f"dev_{timeseries_by}ly"
        sheet_id = "14jUOdsb83EnEmQpXmmLmo3MtCK-CHiZ7bSocOLSjsFo"
        sheet_index = self.get_sheet_index_by_title(sheet_id, sheet_name)
        worksheet = self.gspread_client.open_by_key(sheet_id).get_worksheet(sheet_index)
        row = self.dashboard_row(report_date, timeseries_by)
        if exising_row_index := self.find_existing_row_index(worksheet, row[0], row[1]):
            range_label = f"A{exising_row_index}:L{exising_row_index}"
            worksheet.update(range_label, [row])
        else:
            worksheet.insert_row(
                values=row,
                index=3,
            )


def main():
    import utils

    brands = [
        "Apricot Studios",
        "BLOSSOM",
        "Archivépke",
        "LEMEME",
        "ROH SEOUL",
        "SSIL",
    ]
    brands = ["ROH", "Archivépke"]
    end_date = datetime.date(2026, 5, 10)
    weekly_report_dates = [end_date - datetime.timedelta(days=7 * i) for i in range(7)]
    monthly_report_dates = [datetime.date(2026, 4, 30), datetime.date(2026, 3, 31)]
    for brand in brands:
        client = utils.client(brand)
        for date in reversed(weekly_report_dates):
            print(f"running weekly for {brand} for {date}")
            client.upsert_dashboard_row(date, "week")
        for date in reversed(monthly_report_dates):
            print(f"running monthly for {brand} for {date}")
            client.upsert_dashboard_row(date, "month")


if __name__ == "__main__":
    main()
