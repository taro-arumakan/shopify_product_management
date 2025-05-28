import pprint
import utils


def main():
    client = utils.client("apricot-studios")
    products = client.products_by_collection_handle("25-summer-2nd")
    for p in products:
        new_tags = [
            "25_summer_2nd" if t.upper() == "5/30(2ND)" else t for t in p["tags"]
        ] + ["campaign_eligible"]
        print(["title"], new_tags)
        pprint.pprint(client.update_product_tags(p["id"], ",".join(new_tags)))


if __name__ == "__main__":
    main()
