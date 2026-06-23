import calendar
import datetime
import logging
import os
import tempfile

logger = logging.getLogger(__name__)


class GaReportingInterface:
    """Google Analytics 4 (Data API) reports for the monthly brand report.

    Pulls what Shopify can't: channel-level engagement (engagement rate, average
    session duration, key events) and device split. Reads through the same Google
    service account as Drive/Sheets (granted Viewer on the GA account); requires
    the analytics.readonly scope and the Analytics Data API enabled.
    """

    # GA4 property id per brand. Non-secret config (visible in the GA UI), all
    # under the one account (sniarti.fi / 321031756), so kept inline like the IG
    # account map rather than per-brand env vars.
    GA_PROPERTY_ID_BY_BRAND = {
        "Apricot Studios": "491529588",
        "BLOSSOM": "515230768",
        "Archivépke": "449380963",
        "LEMEME": "515216277",
        "ROH SEOUL": "449401564",
        "SSIL": "515239062",
    }

    # (report name, breakdown dimensions, metrics). A time dimension (yearMonth /
    # date) is prepended per window, mirroring the Shopify monthly + daily pattern.
    GA_REPORTS = [
        (
            "GA acquisition by channel",
            ["sessionDefaultChannelGroup"],
            [
                "sessions",
                "totalUsers",
                "newUsers",
                "engagedSessions",
                "engagementRate",
                "averageSessionDuration",
                "keyEvents",
            ],
        ),
        (
            "GA engagement overview",
            [],
            [
                "sessions",
                "totalUsers",
                "newUsers",
                "engagedSessions",
                "engagementRate",
                "averageSessionDuration",
                "userEngagementDuration",
                "screenPageViews",
                "keyEvents",
            ],
        ),
        (
            "GA by device",
            ["deviceCategory"],
            ["sessions", "engagedSessions", "engagementRate"],
        ),
    ]

    def ga_property_id(self, brand_name):
        return self.GA_PROPERTY_ID_BY_BRAND.get(brand_name)

    def ga_run_report(
        self, property_id, date_from, date_to, dimensions, metrics, time_dimension
    ):
        """Run one GA4 report, returning flat row dicts.

        ``time_dimension`` is 'yearMonth' (monthly series) or 'date' (daily); it is
        prepended to the breakdown dimensions and normalised to an ISO ``month``
        (YYYY-MM-01) or ``date`` (YYYY-MM-DD) column so the output matches the rest
        of the pipeline.
        """
        time_col = "month" if time_dimension == "yearMonth" else "date"
        dims = [time_dimension] + list(dimensions)
        body = {
            "dateRanges": [
                {"startDate": f"{date_from:%Y-%m-%d}", "endDate": f"{date_to:%Y-%m-%d}"}
            ],
            "dimensions": [{"name": d} for d in dims],
            "metrics": [{"name": m} for m in metrics],
            "orderBys": [{"dimension": {"dimensionName": time_dimension}}],
            "limit": 100000,
        }
        rows = []
        offset = 0
        while True:
            body["offset"] = offset
            res = (
                self.analytics_data_service.properties()
                .runReport(property=f"properties/{property_id}", body=body)
                .execute()
            )
            data = res.get("rows", [])
            for r in data:
                dv = r["dimensionValues"]
                raw = dv[0]["value"]
                if time_dimension == "yearMonth":
                    tval = f"{raw[:4]}-{raw[4:6]}-01"
                else:
                    tval = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
                row = {time_col: tval}
                for name, v in zip(dimensions, dv[1:]):
                    row[name] = v["value"]
                for name, v in zip(metrics, r["metricValues"]):
                    row[name] = v["value"]
                rows.append(row)
            offset += len(data)
            if not data or offset >= int(res.get("rowCount", 0)):
                break
        return rows

    def extract_ga_reports(
        self, report_year, report_month, brand_name=None, local_dir=None, upload=True
    ):
        """Extract the GA4 reports as seed CSVs: a 13-month monthly series and a
        daily series for the report month, mirrored to Drive under
        MONTHLY_EXTRACTION_FOLDER_ID/<YYYYMM>/<brand>/GA/.

        Returns the written paths, or [] for brands without a GA property.
        """
        brand_name = brand_name or getattr(self, "BRAND_NAME", None)
        assert brand_name, "brand_name is required (no BRAND_NAME on this client)"
        property_id = self.ga_property_id(brand_name)
        if not property_id:
            logger.info(
                f"{self.__class__.__name__} no GA property for {brand_name}; "
                f"skipping GA"
            )
            return []

        month_end = datetime.date(
            report_year,
            report_month,
            calendar.monthrange(report_year, report_month)[1],
        )
        month_start = datetime.date(report_year, report_month, 1)
        yoy_start = datetime.date(report_year - 1, report_month, 1)
        period = f"{report_year}{report_month:02d}"

        local_dir = local_dir or os.path.join(
            tempfile.gettempdir(),
            "monthly_extraction",
            brand_name.replace(" ", "_"),
            period,
            "GA",
        )
        os.makedirs(local_dir, exist_ok=True)

        drive_folder_id = None
        if upload:
            drive_folder_id = self._find_or_create_folder_path(
                self.MONTHLY_EXTRACTION_FOLDER_ID, period, brand_name, "GA"
            )

        # (time dimension, date_from, date_to, filename suffix)
        windows = [
            ("yearMonth", yoy_start, month_end, ""),
            ("date", month_start, month_end, " - daily"),
        ]
        written = []
        for name, dims, metrics in self.GA_REPORTS:
            for time_dim, date_from, date_to, suffix in windows:
                rows = self.ga_run_report(
                    property_id, date_from, date_to, dims, metrics, time_dim
                )
                time_col = "month" if time_dim == "yearMonth" else "date"
                fieldnames = [time_col] + list(dims) + list(metrics)
                filename = (
                    f"{name}{suffix} - {date_from:%Y-%m-%d} - {date_to:%Y-%m-%d}.csv"
                )
                output_path = os.path.join(local_dir, filename)
                self.write_dicts_to_csv(rows, output_path, fieldnames=fieldnames)
                if upload:
                    self.replace_or_upload_to_drive(
                        output_path, "text/csv", drive_folder_id
                    )
                written.append(output_path)
        logger.info(
            f"{self.__class__.__name__} extracted {len(written)} GA reports for "
            f"{brand_name} {period}"
        )
        return written
