import datetime
import logging
from brands.apricotstudios.client import ApricotStudiosClient

logging.basicConfig(level=logging.INFO)


def main():
    client = ApricotStudiosClient(
        "gid://shopify/Product/9344675578112",
        product_detail_images_folder_id="1gXZGa5C6Zlg7X-icBsHfk0u6CYgibQpW",
        product_sheet_start_row=2
    )
    sheet_name = "[Spring_2nd] 3/25"

    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 3, 25, 10, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    client.sanity_check_sheet(sheet_name)
    client.process_sheet_to_products(
        sheet_name,
        additional_tags=["26_Spring_Babycot", "New Arrival"],
        scheduled_time=scheduled_time,
    )


def reprocess():
    """after creating failed products, reprocess required fields"""
    client = ApricotStudiosClient(
        "gid://shopify/Product/9344675578112",
        product_detail_images_folder_id="1fCXufym34XgTt80wq0ADVrQ-3SWXZQIZ",
    )
    sheet_name = "[Spring_1st] 2/25"
    product_inputs = client.product_inputs_by_sheet_name(sheet_name)

    import zoneinfo

    scheduled_time = datetime.datetime(
        2026, 2, 25, 10, 0, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
    )

    for product_input in product_inputs:
        product_id = client.product_id_by_title(product_input["title"])
        client.update_description_include_metafield_values(product_id)
    client.update_stocks(product_inputs)
    client.publish_products(product_inputs, scheduled_time=scheduled_time)
    client.post_process_product_inputs(product_inputs)


def set_price():
    client = ApricotStudiosClient()
    sheet_name = "[Spring_1st] 2/25"
    product_inputs = client.product_inputs_by_sheet_name(sheet_name)
    q = " OR ".join(f"title:'{pi['title']}'" for pi in product_inputs)
    products = client.products_by_query(q)
    new_prices_by_variant_id = {
        v["id"]: int(int(v["price"]) * 0.9)
        for p in products
        for v in p["variants"]["nodes"]
    }
    client.update_product_prices_by_dict(
        products, new_prices_by_variant_id=new_prices_by_variant_id, testrun=False
    )


if __name__ == "__main__":
    main()
    # reprocess()
    # set_price()
