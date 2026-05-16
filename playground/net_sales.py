import datetime
import utils

brands = [
    "GBH",
    "ROH",
    "Archivepke",
    "KUME",
    "ApricotStudios",
    "BLOSSOM",
    "LEMEME",
    "SSIL",
    "A&ST",
]

net_sales_by_brand = {}
for brand in brands:
    client = utils.client(brand)
    net_sales_by_brand[brand] = client.report_sales_kpi_by(
        datetime.date(2026, 4, 1), datetime.date(2026, 4, 30)
    ).iloc[0]["net_sales"]

for b, n in net_sales_by_brand.items():
    print(f"{n}")
