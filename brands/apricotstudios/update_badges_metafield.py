import pprint
import utils


def main():
    client = utils.client("apricot-studios")
    products = client.products_by_collection_handle("25-summer-2nd")
    for p in products:
        pprint.pprint(client.update_badges_metafield(p["id"], ["キャンペーン対象"]))


if __name__ == "__main__":
    main()
