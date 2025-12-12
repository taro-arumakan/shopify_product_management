series_names = [
    "AHTO",
    "AIL",
    "AMO",
    "BAILEY",
    "BERT",
    "BETTER",
    "BON",
    "BRIN",
    "CHAO",
    "COLIN",
    "COMMI",
    "DAS",
    "DELF",
    "DEW",
    "DILL ",
    "DIN",
    "DOLPH",
    "FELLA ",
    "FLO",
    "FOTA ",
    "GAEIL",
    "GENTO",
    "GOUF",
    "HARRY",
    "HIMA",
    "KELSEY",
    "KEN",
    "KINDER",
    "KITTEN",
    "KOKA",
    "KYRA",
    "LEVA",
    "RORA",
    "ROTHY",
    "SANA",
    "SEER",
    "SHEARING",
    "SOFFI",
    "SUEDE",
    "TAMI",
    "TENS",
    "TEO",
    "TIA",
    "TIEN",
    "TOBLE",
    "TOSCANA",
    "TOV",
    "TUS",
    "US",
    "VEIN",
    "VERO",
]

import utils

client = utils.client("blossom")
products = client.products_by_query("status:'ACTIVE'")
products_by_series_names = {}
for product in products:
    for series_name in series_names:
        if series_name in map(str.upper, product["title"].split(" ")):
            products_by_series_names.setdefault(series_name, []).append(product)
            break

for series_name, products in products_by_series_names.items():
    print(f"{series_name}: {len(products)}")
    for product in products:
        print(f"    - {product['title']}")
