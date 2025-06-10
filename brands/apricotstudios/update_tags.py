import pprint
import utils


def main():
    client = utils.client("apricot-studios")
    products = client.products_by_tag("2025-06-11")
    for p in products:
        new_tags = p["tags"] + ["25 Summer Swim & Rain"]
        print(["title"], new_tags)
        pprint.pprint(client.update_product_tags(p["id"], ",".join(new_tags)))


if __name__ == "__main__":
    main()
