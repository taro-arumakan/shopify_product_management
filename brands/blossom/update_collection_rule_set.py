import logging

logging.basicConfig(level=logging.INFO)
import utils

collection_names = [
    "ALL",
    "OUTER",
    "TOPS",
    "PANTS",
    "SKIRT",
    "BAG",
    "SHOES",
    "ACC",
]

# collection_names = [
#     "TEST",
#     "TEST2"
# ]


def main():
    client = utils.client("blossom")
    new_rule = {"column": "TAG", "relation": "NOT_EQUALS", "condition": "25FW"}
    for name in collection_names:
        collection = client.collection_by_title(name)
        rule_set = collection["ruleSet"]
        if new_rule not in rule_set["rules"]:
            rule_set["rules"].append(new_rule)
        rule_set["appliedDisjunctively"] = False
        logging.info(f"updating {collection['title']}: {rule_set}")
        client.collection_update_rule_set(collection["id"], rule_set=rule_set)


if __name__ == "__main__":
    main()
