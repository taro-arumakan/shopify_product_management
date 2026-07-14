import datetime
import logging
import sys
import zoneinfo
import utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
for noisy in ("googleapiclient", "urllib3", "google"):
    logging.getLogger(noisy).setLevel(logging.WARNING)


def get_report_date(term):
    run_date = datetime.datetime.today().astimezone(zoneinfo.ZoneInfo("Asia/Tokyo"))
    if term == "week":
        return (run_date - datetime.timedelta((run_date.weekday() + 1))).date()
    elif term == "month":
        return datetime.date(run_date.year, run_date.month, 1) - datetime.timedelta(
            days=1
        )


def main():
    term = sys.argv[1]

    brands = [
        "Apricot Studios",
        "BLOSSOM",
        "KUMÉ",
        "LEMEME",
        "ROH SEOUL",
        "SSIL",
    ]
    report_date = get_report_date(term)

    failures = []
    for brand in brands:
        logging.info(f"running {term}ly for {brand} for {report_date}")
        try:
            client = utils.client(brand)
            client.upsert_dashboard_row(report_date, term)
        except Exception as e:
            logging.exception(f"{term}ly dashboard failed for {brand}: {e}")
            failures.append(brand)

    if failures:
        raise SystemExit(f"dashboard update failed for: {', '.join(failures)}")


if __name__ == "__main__":
    main()
