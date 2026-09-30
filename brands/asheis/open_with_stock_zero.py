import datetime
import zoneinfo
import utils


def iq_by_sku_oct_1st():
    return {
        "21263430302400": 30,
        "21263430302700": 20,
        "21263430290600": 48,
        "21263430292400": 38,
        "21263430292700": 27,
        "21263410230100": 40,
        "21263410232700": 35,
        "21263470372400": 35,
        "21263470372700": 15,
        "21263110372400": 45,
        "21263110372700": 30,
        "21263410372400": 40,
        "21263410372700": 35,
        "21263210151200": 13,
        "21263210152700": 25,
        "21263410225700": 28,
        "21263410222100": 47,
        "21263110131291": 4,
        "21263110131292": 1,
        "21263110132491": 7,
        "21263110132492": 3,
        "21263110132791": 7,
        "21263110132792": 3,
        "21263430342400": 38,
        "21263430342700": 25,
        "21263110142191": 10,
        "21263110142192": 4,
        "21263110142491": 17,
        "21263110142492": 7,
        "21263010021200": 37,
        "21263010025800": 38,
        "21263610030190": 30,
        "21263610030191": 14,
        "21263610035890": 23,
        "21263610035891": 8,
        "21263610041290": 13,
        "21263610041291": 9,
        "21263610042490": 30,
        "21263610042491": 11,
        "21263010071291": 12,
        "21263010071292": 4,
        "21263010072791": 17,
        "21263010072792": 5,
        "21263210021291": 18,
        "21263210021292": 7,
        "21263210025891": 18,
        "21263210025892": 7,
        "21263210071291": 8,
        "21263210071292": 5,
        "21263210072791": 14,
        "21263210072792": 11,
    }


def iq_by_sku_oct_14th():
    return {
        "21263430310100": 34,
        "21263430310600": 15,
        "21263430312500": 25,
        "21263430312700": 26,
        "21263430320100": 33,
        "21263430320600": 18,
        "21263430322500": 24,
        "21263430322700": 25,
        "21263530390600": 10,
        "21263530392500": 20,
        "21263530392700": 15,
    }


def iq_by_sku_nov_4th():
    return {
        "21263430355700": 20,
        "21263430351300": 20,
        "21263430352400": 20,
        "21263430353700": 15,
        "21263430365700": 22,
        "21263430361300": 15,
        "21263430362400": 23,
        "21263430363700": 15,
    }


def original_inventoryQuantity_by_sku(run_date_yyyymmdd):
    mapping = {
        "20261001": iq_by_sku_oct_1st,
        "20261014": iq_by_sku_oct_14th,
        "20261104": iq_by_sku_nov_4th,
    }
    return mapping[run_date_yyyymmdd]()


def revert_stocks(dry_run=True, run_date_yyyymmdd=None):
    client = utils.client("ASHEIS")
    stock_by_sku = original_inventoryQuantity_by_sku(run_date_yyyymmdd)

    location_id = client.location_id_by_name(client.LOCATIONS[0])
    variants = client.variants_by_skus(stock_by_sku.keys())
    for v in variants:
        if not dry_run:
            client.set_inventory_quantity_by_sku_and_location_id(
                v["sku"], location_id, stock_by_sku[v["sku"]]
            )
        else:
            print(f"update {v['sku']} to {stock_by_sku[v['sku']]}")


def nullify_stocks_and_publish(client, products, launch_datetime, dry_run=True):
    for p in products:
        for v in p["variants"]["nodes"]:
            print(f"'{v['sku']}': {v['inventoryQuantity']},")

    if not dry_run:
        location_id = client.location_id_by_name(client.LOCATIONS[0])
        for p in products:
            for v in p["variants"]["nodes"]:
                client.set_inventory_quantity_by_sku_and_location_id(
                    v["sku"], location_id, 0
                )
            client.update_product_metafield(
                p["id"], "custom", "launch_datetime", launch_datetime.isoformat()
            )
            client.update_product_tags(
                p["id"], ",".join(p["tags"] + [f"{launch_datetime:%Y%m%d}"])
            )
            client.publish_by_product_or_collection_id(p["id"], online_store_only=True)


def main():
    client = utils.client("ASHEIS")
    client.product_sheet_start_row = 1
    product_inputs = client.product_inputs_by_sheet_name("【10/14デリ】Products Master")
    launch_datetime_map = {
        None: datetime.datetime(
            2026, 10, 1, 12, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
        ),
        "10/14デリ": datetime.datetime(
            2026, 10, 14, 12, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
        ),
        "11/４デリ予定": datetime.datetime(
            2026, 11, 4, 12, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
        ),
    }
    products = client.products_by_tag("26_oct_2")
    for r, ldt in launch_datetime_map.items():
        print(r or "10/01")
        titles = [pi["title"] for pi in product_inputs if pi.get("remarks") == r]
        nullify_stocks_and_publish(
            client, [p for p in products if p["title"] in titles], ldt, dry_run=True
        )


if __name__ == "__main__":
    main()
