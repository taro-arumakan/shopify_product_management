import pathlib
import utils


def main():
    brands = ["apricot", "blossom", "archive", "gbh", "kume", "lememe", "roh", "ssil"]
    base_dir = pathlib.Path(__file__).resolve().parent
    print(base_dir)
    template_path = f"{base_dir}/monthly_report_template.xlsx"
    year_months = [(2025, 12), (2026, 1)]
    for brand in brands:
        client = utils.client(brand)
        for year_month in year_months:
            client.generate_monthly_report(template_path, *year_month)


if __name__ == "__main__":
    main()
