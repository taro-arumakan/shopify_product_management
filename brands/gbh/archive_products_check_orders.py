import datetime
import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    created_after = datetime.date(2025, 6, 1)

    client = utils.client("gbh")
    for tag in ["24fall", "24 winter"]:
        products = client.products_by_tag(tag)
        products = [p for p in products if not any("25" in t for t in p["tags"])]
        print(f"tag:{tag}: {len(products)}")
        for p in products:
            print(p["title"])
            for v in p["variants"]["nodes"]:
                print(f"\t{v['sku']}")
                orders = client.orders_by_sku(
                    v["sku"], created_after_date=created_after
                )
                for order in orders:
                    print(f"\t\torder at {order['createdAt']}")


if __name__ == "__main__":
    main()
