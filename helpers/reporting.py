class Reporting:

    SLIDES_TEMPLATE_ID = "1jhxdJvbCrF3dozSi819lbkAKt9N45zqjfeNvAddsCxI"
    LOGO_FOLDER_ID = "1tGmwEe0dJrWuVHtnUqnxU3bxbIO0JJoB"
    MONTHLY_IMAGES_FOLDER_ID = "13e7ejhsYGaelUwwteM3SC6_aMrhEsZW4"
    MONTHLY_REPORT_OUTPUT_FOLDER_ID = "1WCmMFHnFBnSin439p1OGFEyQdgDr9lNh"

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

    def generate_monthly_brand_report(self, brand_name, report_year, report_month):
        destination_folder_id = self.find_or_create_folder_by_name(
            self.MONTHLY_REPORT_OUTPUT_FOLDER_ID,
            f"{str(report_year).zfill(2)}{str(report_month).zfill(2)}",
        )
        copy_title = f"[{brand_name}] {report_year}.{report_month} Review and Strategic Recommendations"
        body = {
            "name": copy_title,
            "parents": [destination_folder_id],  #'1ECtC8vKGYuV1hyDvVlEqe-pGwBMeasEz'],
            "supportsAllDrives": True,
        }
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

        # 3. Define Replacements
        # Note: Slides API requires image URLs. You'll need to upload local PNGs
        # to a temporary public URL or a Google Cloud Storage bucket first.
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

        graphs_names = [
            "store_kpi_graph",
            "sales_by_product_graph",
            "customer_type_donut",
            "conversion_breakdown",
        ]

        alt_text_file_id_map = {
            graph_name: self.get_graph_image_id(
                report_year=report_year,
                report_month=report_month,
                brand_name=brand_name,
                graph_name=graph_name,
            )
            for graph_name in graphs_names
        }
        alt_text_file_id_map.update(brand_logo=self.get_logo_image_id(brand_name))

        presentation = (
            self.slides_service.presentations()
            .get(presentationId=presentation_id)
            .execute()
        )

        for slide in presentation.get("slides", []):
            for element in slide.get("pageElements", []):
                alt_text = element.get("description", "")
                if alt_text in alt_text_file_id_map:
                    requests.append(
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

        try:
            for file_id in alt_text_file_id_map.values():
                self.make_public_by_file_id(file_id)

            self.slides_service.presentations().batchUpdate(
                presentationId=presentation_id, body={"requests": requests}
            ).execute()

        finally:
            for file_id in alt_text_file_id_map.values():
                self.make_private_by_file_id(file_id)


def main():
    import utils

    client = utils.client("blossom")
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
        client.generate_monthly_brand_report(brand, 2026, 2)


if __name__ == "__main__":
    main()
