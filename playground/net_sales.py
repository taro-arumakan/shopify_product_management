import datetime
import utils

brands = [
    "ROH",
    "KUME",
    "ApricotStudios",
    "BLOSSOM",
    "LEMEME",
    "SSIL",
    "A&ST",
    "ASHEIS",
    "GBH",
    "Archivepke",
]

net_sales_by_brand = {}
for brand in brands:
    client = utils.client(brand)
    net_sales_by_brand[brand] = client.report_sales_kpi_by(
        datetime.date(2026, 7, 1), datetime.date(2026, 7, 31)
    ).iloc[0]["net_sales"]

for b, n in net_sales_by_brand.items():
    print(f"{n}")
