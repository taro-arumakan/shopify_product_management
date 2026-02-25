import logging
from brands.rohseoul.client import RohseoulClient

logging.basicConfig(level=logging.INFO)


def main():
    handle_suffix = "26ss-1rd"

    client = RohseoulClient()
    sheet_name = "26ss 1rd(NEW)"
    client.sanity_check_sheet(sheet_name, handle_suffix=handle_suffix)
    # client.process_sheet_to_products(
    #     sheet_name=sheet_name,
    #     handle_suffix=handle_suffix,
    #     additional_tags=["26_spring", "New Arrival"],
    # )


if __name__ == "__main__":
    main()
