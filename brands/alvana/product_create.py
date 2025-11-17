import logging
from brands.alvana.client import AlvanaClient

logging.basicConfig(level=logging.INFO)


def main():

    client = AlvanaClient()
    client.process_sheet_to_products("5G LAMS WOOL ZIP UP KNIT")


if __name__ == "__main__":
    main()
