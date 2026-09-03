import logging

logging.basicConfig(level=logging.INFO)
import utils

# Category collections that should only ever surface the current season.
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

# Season tags a category collection may have been pinned to in an earlier season.
# They get dropped so the rule sets stay flat instead of growing an exclusion per season.
season_tags = ["24PF", "25SS", "25PF", "25FW", "25WI", "26PS", "26SS", "26FW"]

current_season_tag = "26FW"


def is_season_rule(rule):
    return rule["column"] == "TAG" and rule["condition"] in season_tags


def switch_categories_to_26fw():
    """Show only 26FW products on the category collections, and move the
    still-on-sale spring/summer products under the 26SS collection.

    Runs at open time (9/4 18:00 JST) via the Shopify Flow that dispatches
    run_func.yml. Idempotent: rerunning it produces the same rule sets.
    """
    client = utils.client("blossom")
    season_rule = {
        "column": "TAG",
        "relation": "EQUALS",
        "condition": current_season_tag,
    }

    for name in collection_names:
        collection = client.collection_by_title(name)
        rule_set = collection["ruleSet"]
        rules = [r for r in rule_set["rules"] if not is_season_rule(r)]
        rules.append(season_rule)
        rule_set["rules"] = rules
        rule_set["appliedDisjunctively"] = False
        logging.info(f"updating {collection['title']}: {rule_set}")
        client.collection_update_rule_set(collection["id"], rule_set=rule_set)

    # The 26SS collection was still pinned to the 2026_drop1-8 tags, which are the
    # 26PS products. Point it at the season tags so every spring/summer product
    # that is still on sale stays reachable from the 26SS entry.
    collection = client.collection_by_title("26SS")
    rule_set = {
        "rules": [
            {"column": "TAG", "relation": "EQUALS", "condition": "26SS"},
            {"column": "TAG", "relation": "EQUALS", "condition": "26PS"},
        ],
        "appliedDisjunctively": True,
    }
    logging.info(f"updating {collection['title']}: {rule_set}")
    client.collection_update_rule_set(collection["id"], rule_set=rule_set)


if __name__ == "__main__":
    switch_categories_to_26fw()
