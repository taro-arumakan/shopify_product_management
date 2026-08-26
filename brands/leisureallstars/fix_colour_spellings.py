"""Correct misspelt colour names on live EPOKHE products.

Three colourways carry a misspelling in their option value, which is the text a
customer sees on the product page: POLOSHED for POLISHED on two, and MATT for
MATTE on one. The order sheet has been corrected at source; this brings the
store into line.

Only unambiguous misspellings are touched. Notably SMOKE is **not** one of them
-- EPOKHE writes both "Beige Smoke Polished" and "Smoked Crystal Polished" on
different colourways, so neither form is wrong.

The colour code is unchanged by every fix here (POLOSHED and POLISHED both
collapse to P, MATT and MATTE both to M), so no product title moves. The
``global.title_tag`` metafield does embed the colour, so it is rewritten.

    python -m brands.leisureallstars.fix_colour_spellings          # report only
    python -m brands.leisureallstars.fix_colour_spellings --apply  # write
"""

import logging
import sys

import utils

logger = logging.getLogger(__name__)

VENDOR = "EPOKHE"

#: Misspelling -> correction. Applied whole-word, case-insensitively.
CORRECTIONS = {
    "POLOSHED": "Polished",
    "PORALIZED": "Polarized",
    "POLARISED": "Polarized",
    "MATT": "Matte",
}

OPTION_UPDATE = """
mutation updateOptionValue(
    $productId: ID!, $option: OptionUpdateInput!, $values: [OptionValueUpdateInput!]
) {
    productOptionUpdate(
        productId: $productId, option: $option, optionValuesToUpdate: $values
    ) {
        product { id options { name optionValues { id name } } }
        userErrors { field message }
    }
}
"""


def corrected(colour):
    """Return the corrected colour string, or None when nothing needs fixing."""
    words = colour.split()
    fixed = [CORRECTIONS.get(word.upper().strip(",-"), word) for word in words]
    result = " ".join(fixed)
    return None if result == colour else result


def build_plan(client):
    plan = []
    for product in client.products_by_query(f"vendor:'{VENDOR}'"):
        for variant in product["variants"]["nodes"]:
            for selected in variant["selectedOptions"]:
                fix = corrected(selected["value"])
                if not fix:
                    continue
                plan.append(
                    {
                        "product_id": product["id"],
                        "title": product["title"],
                        "option_name": selected["name"],
                        "old": selected["value"],
                        "new": fix,
                    }
                )
    return plan


def apply_plan(client, plan, testrun=True):
    for row in plan:
        if testrun:
            logger.info(f"would fix {row['old']!r} -> {row['new']!r} on {row['title']}")
            continue
        product = client.run_query(
            query='{ product(id: "%s") { options { id name optionValues { id name } } } }'
            % row["product_id"]
        )["product"]
        option = next(o for o in product["options"] if o["name"] == row["option_name"])
        value = next(v for v in option["optionValues"] if v["name"] == row["old"])
        res = client.run_query(
            query=OPTION_UPDATE,
            variables={
                "productId": row["product_id"],
                "option": {"id": option["id"]},
                "values": [{"id": value["id"], "name": row["new"]}],
            },
        )
        if errors := res["productOptionUpdate"]["userErrors"]:
            raise RuntimeError(f"failed on {row['title']}: {errors}")
        client.update_product_metafield(
            row["product_id"], "global", "title_tag", f"{row['title']} - {row['new']}"
        )
        logger.info(f"fixed {row['old']!r} -> {row['new']!r} on {row['title']}")


def main(testrun=True):
    logging.basicConfig(level=logging.INFO)
    client = utils.client("leisureallstars")
    plan = build_plan(client)
    print(f"colour values needing a fix: {len(plan)}")
    for row in plan:
        print(f"    {row['title']:28} {row['old']!r}  ->  {row['new']!r}")
    apply_plan(client, plan, testrun=testrun)
    return plan


if __name__ == "__main__":
    main(testrun="--apply" not in sys.argv)
