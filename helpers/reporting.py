import calendar
import csv
import datetime
import logging
import os
import tempfile
import pandas as pd
import pprint

logger = logging.getLogger(__name__)


class Reporting:

    SLIDES_TEMPLATE_ID = "1jhxdJvbCrF3dozSi819lbkAKt9N45zqjfeNvAddsCxI"
    LOGO_FOLDER_ID = "1tGmwEe0dJrWuVHtnUqnxU3bxbIO0JJoB"
    MONTHLY_IMAGES_FOLDER_ID = "13e7ejhsYGaelUwwteM3SC6_aMrhEsZW4"
    MONTHLY_REPORT_OUTPUT_FOLDER_ID = "1WCmMFHnFBnSin439p1OGFEyQdgDr9lNh"
    # Seed data extracted for the staff's monthly brand reports, organised as
    # <MONTHLY_EXTRACTION_FOLDER_ID>/<YYYYMM>/<brand>/Shopify/<report>.csv
    MONTHLY_EXTRACTION_FOLDER_ID = "1qiX0MMtnrbF1irJX9_NXBTeQb4LpMFk4"

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

    def extract_shopify_analytics_reports(
        self, report_year, report_month, brand_name=None, local_dir=None, upload=True
    ):
        """Extract every Shopify Admin -> Analytics report as seed CSVs for a brand.

        Produces, per report: a 13-month series (year-over-year comparison) and a
        daily series for the report month (so the latest month can be traced). Files
        are written locally and, when ``upload``, mirrored to Google Drive under
        ``MONTHLY_EXTRACTION_FOLDER_ID``/<YYYYMM>/<brand>/Shopify/.
        """
        brand_name = brand_name or getattr(self, "BRAND_NAME", None)
        assert brand_name, "brand_name is required (no BRAND_NAME on this client)"

        month_end = datetime.date(
            report_year,
            report_month,
            calendar.monthrange(report_year, report_month)[1],
        )
        month_start = datetime.date(report_year, report_month, 1)
        # 13 months: same month last year .. report month, for YoY comparison
        yoy_start = datetime.date(report_year - 1, report_month, 1)
        windows = [
            ("month", yoy_start, month_end),
            ("day", month_start, month_end),
        ]

        period = f"{report_year}{report_month:02d}"
        local_dir = local_dir or os.path.join(
            tempfile.gettempdir(),
            "monthly_extraction",
            brand_name.replace(" ", "_"),
            period,
            "Shopify",
        )
        os.makedirs(local_dir, exist_ok=True)

        drive_folder_id = None
        if upload:
            period_folder = self.find_or_create_folder_by_name(
                self.MONTHLY_EXTRACTION_FOLDER_ID, period
            )
            brand_folder = self.find_or_create_folder_by_name(period_folder, brand_name)
            drive_folder_id = self.find_or_create_folder_by_name(
                brand_folder, "Shopify"
            )

        written = []
        for timeseries_by, date_from, date_to in windows:
            queries = self.analytics_export_queries(date_from, date_to, timeseries_by)
            for name, query in queries.items():
                suffix = "" if timeseries_by == "month" else " - daily"
                filename = (
                    f"{name}{suffix} - {date_from:%Y-%m-%d} - {date_to:%Y-%m-%d}.csv"
                )
                output_path = os.path.join(local_dir, filename)
                logger.info(f"{self.__class__.__name__} extracting {filename}")
                self.write_analytics_report_csv(query, output_path)
                if upload:
                    self.replace_or_upload_to_drive(
                        output_path, "text/csv", drive_folder_id
                    )
                written.append(output_path)
        logger.info(
            f"{self.__class__.__name__} extracted {len(written)} Shopify reports for "
            f"{brand_name} {period}"
        )
        return written

    @staticmethod
    def write_dicts_to_csv(rows, output_path, fieldnames=None):
        """Write a list of flat dicts to CSV (UTF-8 BOM for clean Excel reads)."""
        fieldnames = fieldnames or (list(rows[0].keys()) if rows else [])
        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return output_path

    def extract_meta_ads_reports(
        self, report_year, report_month, brand_name=None, local_dir=None, upload=True
    ):
        """Extract Meta (Ad Manager) ad-level insights as seed CSVs for a brand.

        One CSV combines every metric the staff used to export across two presets
        (performance/clicks + conversions/ROAS). Produces a 13-month monthly series
        (year-over-year) and a daily series for the report month. Files mirror to
        Drive under MONTHLY_EXTRACTION_FOLDER_ID/<YYYYMM>/<brand>/Meta/.
        """
        brand_name = brand_name or getattr(self, "BRAND_NAME", None)
        assert brand_name, "brand_name is required (no BRAND_NAME on this client)"

        month_end = datetime.date(
            report_year,
            report_month,
            calendar.monthrange(report_year, report_month)[1],
        )
        month_start = datetime.date(report_year, report_month, 1)
        yoy_start = datetime.date(report_year - 1, report_month, 1)
        # (filename granularity label, time_increment, date_from, date_to)
        windows = [
            ("monthly", "monthly", yoy_start, month_end),
            ("daily", 1, month_start, month_end),
        ]

        period = f"{report_year}{report_month:02d}"
        local_dir = local_dir or os.path.join(
            tempfile.gettempdir(),
            "monthly_extraction",
            brand_name.replace(" ", "_"),
            period,
            "Meta",
        )
        os.makedirs(local_dir, exist_ok=True)

        drive_folder_id = None
        if upload:
            period_folder = self.find_or_create_folder_by_name(
                self.MONTHLY_EXTRACTION_FOLDER_ID, period
            )
            brand_folder = self.find_or_create_folder_by_name(period_folder, brand_name)
            drive_folder_id = self.find_or_create_folder_by_name(brand_folder, "Meta")

        written = []
        for label, time_increment, date_from, date_to in windows:
            logger.info(
                f"{self.__class__.__name__} extracting Meta ad insights "
                f"({label}) {date_from} .. {date_to}"
            )
            rows = self.ad_insights(date_from, date_to, time_increment=time_increment)
            suffix = "" if label == "monthly" else " - daily"
            filename = f"Meta ads by ad{suffix} - {date_from:%Y-%m-%d} - {date_to:%Y-%m-%d}.csv"
            output_path = os.path.join(local_dir, filename)
            self.write_dicts_to_csv(rows, output_path)
            if upload:
                self.replace_or_upload_to_drive(
                    output_path, "text/csv", drive_folder_id
                )
            written.append(output_path)
        logger.info(
            f"{self.__class__.__name__} extracted {len(written)} Meta reports for "
            f"{brand_name} {period}"
        )
        return written

    IG_METRIC_COLUMNS = [
        "reach",
        "views",
        "profile_views",
        "website_clicks",
        "total_interactions",
        "follows",
    ]

    IG_POST_COLUMNS = [
        "post_id",
        "timestamp",
        "media_type",
        "media_product_type",
        "permalink",
        "caption",
        "like_count",
        "comments_count",
        "reach",
        "views",
        "likes",
        "comments",
        "shares",
        "saved",
        "total_interactions",
        "follows",
        "profile_visits",
        "profile_activity",
    ]

    def extract_instagram_reports(
        self, report_year, report_month, brand_name=None, local_dir=None, upload=True
    ):
        """Extract Instagram account metrics (Business Suite "結果"/Results) as CSVs.

        Replaces the six separate daily exports (reach, views, profile visits, link
        clicks, interactions, follows) with one monthly-totals file over 13 months
        and one daily file for the report month. A single day-by-day pass over the
        13-month window feeds both. 'follows' fills only the trailing 30 days (API
        limit). Stories and post-level content are handled separately.
        """
        brand_name = brand_name or getattr(self, "BRAND_NAME", None)
        assert brand_name, "brand_name is required (no BRAND_NAME on this client)"

        month_end = datetime.date(
            report_year,
            report_month,
            calendar.monthrange(report_year, report_month)[1],
        )
        month_start = datetime.date(report_year, report_month, 1)
        yoy_start = datetime.date(report_year - 1, report_month, 1)

        daily = self.ig_account_metrics_by_day(yoy_start, month_end)
        monthly = self.aggregate_ig_metrics_by_month(daily)
        report_month_daily = [
            r
            for r in daily
            if r["date"].startswith(f"{report_year}-{report_month:02d}")
        ]
        posts = self.ig_posts_with_insights(month_start, month_end)
        format_counts = self.ig_published_format_counts(month_start, month_end)

        # Stories can't be pulled retroactively, so fold in what the daily capture
        # has accumulated for this month (empty for months before the daily job ran).
        month_prefix = f"{report_year}-{report_month:02d}"
        report_stories = [
            s
            for s in self.read_combined_ig_daily(brand_name, "stories")
            if (s.get("timestamp") or "").startswith(month_prefix)
        ]
        format_row = [
            {
                "month": f"{month_start:%Y-%m}",
                "feed_posts": format_counts.get("FEED", 0),
                "reels": format_counts.get("REELS", 0),
                "posts_total": format_counts.get("FEED", 0)
                + format_counts.get("REELS", 0),
                "stories": len(report_stories),
            }
        ]
        story_fieldnames = [
            "capture_date",
            "story_id",
            "timestamp",
            "media_type",
            "media_product_type",
            "permalink",
            "caption",
        ] + self.IG_STORY_METRICS

        period = f"{report_year}{report_month:02d}"
        local_dir = local_dir or os.path.join(
            tempfile.gettempdir(),
            "monthly_extraction",
            brand_name.replace(" ", "_"),
            period,
            "Instagram",
        )
        os.makedirs(local_dir, exist_ok=True)

        drive_folder_id = None
        if upload:
            period_folder = self.find_or_create_folder_by_name(
                self.MONTHLY_EXTRACTION_FOLDER_ID, period
            )
            brand_folder = self.find_or_create_folder_by_name(period_folder, brand_name)
            drive_folder_id = self.find_or_create_folder_by_name(
                brand_folder, "Instagram"
            )

        outputs = [
            (
                f"Instagram account metrics - {yoy_start:%Y-%m-%d} - {month_end:%Y-%m-%d}.csv",
                monthly,
                ["month"] + self.IG_METRIC_COLUMNS,
            ),
            (
                f"Instagram account metrics - daily - {month_start:%Y-%m-%d} - {month_end:%Y-%m-%d}.csv",
                report_month_daily,
                ["date"] + self.IG_METRIC_COLUMNS,
            ),
            (
                f"Instagram posts - {month_start:%Y-%m-%d} - {month_end:%Y-%m-%d}.csv",
                posts,
                self.IG_POST_COLUMNS,
            ),
            (
                f"Instagram stories - {month_start:%Y-%m-%d} - {month_end:%Y-%m-%d}.csv",
                report_stories,
                story_fieldnames,
            ),
            (
                f"Instagram published format counts - {month_start:%Y-%m}.csv",
                format_row,
                ["month", "feed_posts", "reels", "posts_total", "stories"],
            ),
        ]
        written = []
        for filename, rows, fieldnames in outputs:
            output_path = os.path.join(local_dir, filename)
            self.write_dicts_to_csv(rows, output_path, fieldnames=fieldnames)
            if upload:
                self.replace_or_upload_to_drive(
                    output_path, "text/csv", drive_folder_id
                )
            written.append(output_path)
        logger.info(
            f"{self.__class__.__name__} extracted {len(written)} Instagram reports "
            f"for {brand_name} {period}"
        )
        return written

    def _find_or_create_folder_path(self, parent_id, *names):
        """Resolve (creating as needed) a nested folder path, returning the leaf id."""
        folder_id = parent_id
        for name in names:
            folder_id = self.find_or_create_folder_by_name(folder_id, name)
        return folder_id

    def _find_folder_path(self, parent_id, *names):
        """Resolve a nested folder path read-only, returning None if any segment
        is missing (does not create folders)."""
        folder_id = parent_id
        for name in names:
            folder_id = self.find_folder_id_by_name(folder_id, name)
            if not folder_id:
                return None
        return folder_id

    def read_combined_ig_daily(self, brand_name, data_type, local_dir=None):
        """Read the combined daily IG file (account.csv / stories.csv) from Drive.

        Returns a list of row dicts, or [] if the daily capture hasn't produced one
        yet (e.g. backfilled months before the daily job existed).
        """
        ig_folder = self._find_folder_path(
            self.MONTHLY_EXTRACTION_FOLDER_ID, "_daily", brand_name, "Instagram"
        )
        if not ig_folder:
            return []
        match = self.find_by_folder_id_by_name(ig_folder, f"{data_type}.csv")
        if not match:
            return []
        local_dir = local_dir or os.path.join(
            tempfile.gettempdir(), "ig_combine", brand_name.replace(" ", "_")
        )
        os.makedirs(local_dir, exist_ok=True)
        path = os.path.join(local_dir, f"_read_{data_type}.csv")
        self.download_file_from_drive(match["id"], path)
        with open(path, newline="", encoding="utf-8-sig") as fh:
            return list(csv.DictReader(fh))

    def capture_instagram_daily(
        self, capture_date=None, brand_name=None, local_dir=None, upload=True
    ):
        """Capture the perishable Instagram data for one day (run daily via cron).

        Stores, per brand under MONTHLY_EXTRACTION_FOLDER_ID/_daily/<brand>/Instagram/:
          * account/<date>.csv  - the day's account metrics (incl. follows)
          * stories/<date>.csv  - live stories + insights (gone from the API after 24h)

        ``capture_date`` defaults to yesterday in JST. Per-day files keep re-runs
        idempotent; the monthly extraction concatenates and de-dups them later.
        """
        import zoneinfo

        brand_name = brand_name or getattr(self, "BRAND_NAME", None)
        assert brand_name, "brand_name is required (no BRAND_NAME on this client)"
        if capture_date is None:
            capture_date = datetime.datetime.now(
                zoneinfo.ZoneInfo("Asia/Tokyo")
            ).date() - datetime.timedelta(days=1)

        account_row = self.ig_account_metrics_for_day(capture_date)
        stories = self.ig_stories_with_insights()
        for row in stories:
            row["capture_date"] = f"{capture_date:%Y-%m-%d}"

        local_dir = local_dir or os.path.join(
            tempfile.gettempdir(),
            "ig_daily",
            brand_name.replace(" ", "_"),
        )
        account_dir = os.path.join(local_dir, "account")
        stories_dir = os.path.join(local_dir, "stories")
        os.makedirs(account_dir, exist_ok=True)
        os.makedirs(stories_dir, exist_ok=True)

        account_path = os.path.join(account_dir, f"{capture_date:%Y-%m-%d}.csv")
        stories_path = os.path.join(stories_dir, f"{capture_date:%Y-%m-%d}.csv")
        self.write_dicts_to_csv(
            [account_row], account_path, fieldnames=["date"] + self.IG_METRIC_COLUMNS
        )
        story_fields = [
            "capture_date",
            "story_id",
            "timestamp",
            "media_type",
            "media_product_type",
            "permalink",
            "caption",
        ] + self.IG_STORY_METRICS
        self.write_dicts_to_csv(stories, stories_path, fieldnames=story_fields)

        if upload:
            account_folder = self._find_or_create_folder_path(
                self.MONTHLY_EXTRACTION_FOLDER_ID,
                "_daily",
                brand_name,
                "Instagram",
                "account",
            )
            stories_folder = self._find_or_create_folder_path(
                self.MONTHLY_EXTRACTION_FOLDER_ID,
                "_daily",
                brand_name,
                "Instagram",
                "stories",
            )
            self.replace_or_upload_to_drive(account_path, "text/csv", account_folder)
            self.replace_or_upload_to_drive(stories_path, "text/csv", stories_folder)

        logger.info(
            f"{self.__class__.__name__} captured IG daily for {brand_name} "
            f"{capture_date}: account + {len(stories)} stories"
        )
        return [account_path, stories_path]

    def combine_ig_daily_files(self, brand_name=None, local_dir=None):
        """Concatenate the per-day Instagram capture files into one file per type.

        Reads every day-file under _daily/<brand>/Instagram/{account,stories}/ from
        Drive, de-duplicates (account by date, stories by story_id, keeping the
        latest), and writes a single combined CSV alongside them. Lets a consumer
        read one file per brand instead of one per day. Idempotent.
        """
        brand_name = brand_name or getattr(self, "BRAND_NAME", None)
        assert brand_name, "brand_name is required (no BRAND_NAME on this client)"

        ig_folder = self._find_or_create_folder_path(
            self.MONTHLY_EXTRACTION_FOLDER_ID, "_daily", brand_name, "Instagram"
        )
        local_dir = local_dir or os.path.join(
            tempfile.gettempdir(), "ig_combine", brand_name.replace(" ", "_")
        )
        os.makedirs(local_dir, exist_ok=True)

        specs = [
            ("account", "date", ["date"] + self.IG_METRIC_COLUMNS),
            (
                "stories",
                "story_id",
                [
                    "capture_date",
                    "story_id",
                    "timestamp",
                    "media_type",
                    "media_product_type",
                    "permalink",
                    "caption",
                ]
                + self.IG_STORY_METRICS,
            ),
        ]
        written = []
        for data_type, dedup_key, fieldnames in specs:
            subfolder = self.find_folder_id_by_name(ig_folder, data_type)
            if not subfolder:
                continue
            day_files = sorted(
                self.list_files_in_folder(subfolder), key=lambda f: f["name"]
            )
            merged = {}
            for f in day_files:
                tmp = os.path.join(local_dir, f["name"])
                self.download_file_from_drive(f["id"], tmp)
                with open(tmp, newline="", encoding="utf-8-sig") as fh:
                    for row in csv.DictReader(fh):
                        merged[row.get(dedup_key)] = row
            rows = [merged[k] for k in sorted(merged)]
            combined_path = os.path.join(local_dir, f"{data_type}.csv")
            self.write_dicts_to_csv(rows, combined_path, fieldnames=fieldnames)
            self.replace_or_upload_to_drive(combined_path, "text/csv", ig_folder)
            logger.info(
                f"{self.__class__.__name__} combined {len(day_files)} {data_type} "
                f"day-files into {len(rows)} rows for {brand_name}"
            )
            written.append(combined_path)
        return written

    def build_monthly_kpi_rollup(
        self, report_year, report_month, brand_name=None, period_dir=None, upload=True
    ):
        """Combine the three sources into one monthly KPI sheet (13 months).

        Shopify metrics are re-queried (cheap); Meta and Instagram are read from the
        monthly raw CSVs the extractors just wrote (so the costly pulls aren't
        repeated). Saved next to the raw files so reporting can consume either.
        """
        import glob
        from functools import reduce

        brand_name = brand_name or getattr(self, "BRAND_NAME", None)
        assert brand_name, "brand_name is required (no BRAND_NAME on this client)"

        month_end = datetime.date(
            report_year,
            report_month,
            calendar.monthrange(report_year, report_month)[1],
        )
        yoy_start = datetime.date(report_year - 1, report_month, 1)
        period = f"{report_year}{report_month:02d}"
        period_dir = period_dir or os.path.join(
            tempfile.gettempdir(),
            "monthly_extraction",
            brand_name.replace(" ", "_"),
            period,
        )

        def to_month_key(series):
            return series.astype(str).str[:10]

        frames = []

        # Shopify - cheap to re-query, clean column names
        try:
            kpi = self.report_sales_kpi_by(yoy_start, month_end, "month")
            sessions = self.run_shopifyql(
                f"FROM sessions SHOW sessions, conversion_rate TIMESERIES month "
                f"SINCE {yoy_start:%Y-%m-%d} UNTIL {month_end:%Y-%m-%d} ORDER BY month ASC"
            )
            kpi["month"] = to_month_key(kpi["month"])
            sessions["month"] = to_month_key(sessions["month"])
            shop = pd.merge(
                kpi[
                    [
                        "month",
                        "orders",
                        "net_sales",
                        "average_order_value",
                        "returning_customer_rate",
                    ]
                ],
                sessions[["month", "sessions", "conversion_rate"]],
                on="month",
                how="outer",
            )
            frames.append(shop)
        except Exception as e:
            logger.warning(f"{self.__class__.__name__} rollup: Shopify skipped ({e})")

        # Meta - aggregate the per-ad monthly file by month
        meta_files = [
            f
            for f in glob.glob(
                os.path.join(period_dir, "Meta", "Meta ads by ad - *.csv")
            )
            if " - daily - " not in f
        ]
        if meta_files:
            m = pd.read_csv(meta_files[0])
            for col in ["spend", "purchase_value", "purchases"]:
                m[col] = pd.to_numeric(m.get(col), errors="coerce")
            g = (
                m.groupby("report_start")
                .agg(
                    ad_spend=("spend", "sum"),
                    ad_purchase_value=("purchase_value", "sum"),
                    ad_purchases=("purchases", "sum"),
                )
                .reset_index()
                .rename(columns={"report_start": "month"})
            )
            g["ad_roas"] = (g["ad_purchase_value"] / g["ad_spend"]).round(4)
            g["month"] = to_month_key(g["month"])
            frames.append(g)

        # Instagram - monthly account metrics file is already clean
        ig_files = [
            f
            for f in glob.glob(
                os.path.join(
                    period_dir, "Instagram", "Instagram account metrics - *.csv"
                )
            )
            if " - daily - " not in f
        ]
        if ig_files:
            ig = pd.read_csv(ig_files[0])
            ig = ig.rename(columns={c: f"ig_{c}" for c in ig.columns if c != "month"})
            ig["month"] = to_month_key(ig["month"])
            frames.append(ig)

        if not frames:
            logger.warning(f"{self.__class__.__name__} rollup: no sources available")
            return None

        rollup = reduce(
            lambda a, b: pd.merge(a, b, on="month", how="outer"), frames
        ).sort_values("month")

        os.makedirs(period_dir, exist_ok=True)
        out_path = os.path.join(
            period_dir,
            f"Monthly KPI rollup - {yoy_start:%Y-%m} - {month_end:%Y-%m}.csv",
        )
        rollup.to_csv(out_path, index=False, encoding="utf-8-sig")
        if upload:
            brand_folder = self._find_or_create_folder_path(
                self.MONTHLY_EXTRACTION_FOLDER_ID, period, brand_name
            )
            self.replace_or_upload_to_drive(out_path, "text/csv", brand_folder)
        logger.info(
            f"{self.__class__.__name__} built monthly KPI rollup for {brand_name} "
            f"({len(rollup)} months, {len(rollup.columns)} columns)"
        )
        return out_path

    def extract_all_monthly(
        self, report_year, report_month, brand_name=None, upload=True
    ):
        """Extract every source's seed CSVs plus the cross-source KPI rollup.

        Shopify always runs; Meta and Instagram run when the brand has Meta creds.
        Returns a dict of source -> written paths (rollup under 'rollup').
        """
        brand_name = brand_name or getattr(self, "BRAND_NAME", None)
        assert brand_name, "brand_name is required (no BRAND_NAME on this client)"

        paths = {
            "shopify": self.extract_shopify_analytics_reports(
                report_year, report_month, brand_name=brand_name, upload=upload
            )
        }
        if self.meta_ad_account_id and self.meta_token:
            paths["meta"] = self.extract_meta_ads_reports(
                report_year, report_month, brand_name=brand_name, upload=upload
            )
        if self.ig_user_id and self.meta_token:
            paths["instagram"] = self.extract_instagram_reports(
                report_year, report_month, brand_name=brand_name, upload=upload
            )
        paths["rollup"] = self.build_monthly_kpi_rollup(
            report_year, report_month, brand_name=brand_name, upload=upload
        )
        return paths

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
        sheet_name = f"dev_{timeseries_by}ly"
        sheet_id = "14jUOdsb83EnEmQpXmmLmo3MtCK-CHiZ7bSocOLSjsFo"
        sheet_index = self.get_sheet_index_by_title(sheet_id, sheet_name)
        worksheet = self.gspread_client.open_by_key(sheet_id).get_worksheet(sheet_index)
        row = self.dashboard_row(report_date, timeseries_by)
        if exising_row_index := self.find_existing_row_index(worksheet, row[0], row[1]):
            range_label = f"A{exising_row_index}:L{exising_row_index}"
            logger.info(f"updating an existing row {range_label}")
            worksheet.update(range_label, [row])
        else:
            logger.info(f"adding a new row")
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
