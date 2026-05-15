import datetime
import sys
import zoneinfo
import utils


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
        "Archivépke",
        "LEMEME",
        "ROH SEOUL",
        "SSIL",
    ]
    report_date = get_report_date(term)

    for brand in brands:
        client = utils.client(brand)
        print(f"running {term}ly for {brand} for {report_date}")
        client.upsert_dashboard_row(report_date, term)


if __name__ == "__main__":
    main()
