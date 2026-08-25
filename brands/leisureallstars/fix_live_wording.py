"""Bring three live EPOKHE products onto EPOKHE's own wording.

Every SKU on the order sheet also appears on epokhe.co, the brand's own store,
which makes it an authority the sheet can be checked against. Three live
products disagree with it:

* ``WILSON ARMGRNP/BLK`` -- the lens is GREEN, not BLACK. Both the SKU
  (``0916-AGRNPOGRN``) and epokhe.co say so, and no army green / black WILSON
  exists. This one moves the title as well as the option value.
* ``GUILTY x Thomas Towend`` -- the collaborating tattoo artist is Thomas
  **Townend**. Three products carry the misspelling; a fourth colourway is
  still to be created and will use the corrected spelling from the sheet.
* ``DOME GUNMTLP/BLKP`` -- EPOKHE writes GUNMETAL as one word. The colour code
  is unchanged, so only the option value and the SEO tag move.

The order sheet has been corrected at source for all three.

Handles are left alone, as in :mod:`.standardise_titles`, so no product URL
moves. ``global.title_tag`` embeds both title and colour and is rewritten.

    python -m brands.leisureallstars.fix_live_wording          # report only
    python -m brands.leisureallstars.fix_live_wording --apply  # write
"""

import logging
import sys

import utils
from brands.leisureallstars.client import to_shopify_product_title

logger = logging.getLogger(__name__)

VENDOR = "EPOKHE"

#: SKU -> corrected option value. A product not listed here keeps its colour.
COLOUR_FIXES = {
    "0916-AGRNPOGRN": "Army Green Polished / Green",
    "9012-GUNMPOBLKP": "Gunmetal Polished / Black Polarized",
}

#: Substring -> replacement, applied to the style half of a live title.
STYLE_FIXES = {"Thomas Towend": "Thomas Townend"}

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


def fixed_style(title):
    """The style half of a live title with any misspelling corrected."""
    style = title.rsplit(" ", 1)[0]
    for wrong, right in STYLE_FIXES.items():
        style = style.replace(wrong, right)
    return style


def build_plan(client):
    """One row per product needing a change, with old and new for each field."""
    plan = []
    for product in client.products_by_query(f"vendor:'{VENDOR}'"):
        variants = product["variants"]["nodes"]
        if not variants:
            continue
        variant = variants[0]
        sku = (variant["sku"] or "").strip()
        old_colour = variant["title"]
        new_colour = COLOUR_FIXES.get(sku, old_colour)
        style = fixed_style(product["title"])
        # Rebuilt from the corrected colour so the code follows it -- the WILSON
        # fix turns ARMGRNP/BLK into ARMGRNP/GRN without a second rule.
        new_title = to_shopify_product_title(style, new_colour.upper())
        if new_title == product["title"] and new_colour == old_colour:
            continue
        plan.append(
            {
                "id": product["id"],
                "sku": sku,
                "option_name": variant["selectedOptions"][0]["name"],
                "old_title": product["title"],
                "new_title": new_title,
                "old_colour": old_colour,
                "new_colour": new_colour,
            }
        )
    return plan


def _update_option_value(client, row):
    product = client.run_query(
        query='{ product(id: "%s") { options { id name optionValues { id name } } } }'
        % row["id"]
    )["product"]
    option = next(o for o in product["options"] if o["name"] == row["option_name"])
    value = next(v for v in option["optionValues"] if v["name"] == row["old_colour"])
    res = client.run_query(
        query=OPTION_UPDATE,
        variables={
            "productId": row["id"],
            "option": {"id": option["id"]},
            "values": [{"id": value["id"], "name": row["new_colour"]}],
        },
    )
    if errors := res["productOptionUpdate"]["userErrors"]:
        raise RuntimeError(f"failed on {row['old_title']}: {errors}")


def apply_plan(client, plan, testrun=True):
    for row in plan:
        if testrun:
            logger.info(f"would fix {row['old_title']!r} -> {row['new_title']!r}")
            continue
        if row["new_colour"] != row["old_colour"]:
            _update_option_value(client, row)
        if row["new_title"] != row["old_title"]:
            client.update_product_title(row["id"], row["new_title"])
        client.update_product_metafield(
            row["id"],
            "global",
            "title_tag",
            f"{row['new_title']} - {row['new_colour']}",
        )
        logger.info(f"fixed {row['old_title']!r} -> {row['new_title']!r}")


def main(testrun=True):
    logging.basicConfig(level=logging.INFO)
    client = utils.client("leisureallstars")
    plan = build_plan(client)
    print(f"products to fix: {len(plan)}")
    for row in plan:
        print(f"    {row['old_title']:34} -> {row['new_title']}")
        if row["new_colour"] != row["old_colour"]:
            print(f"    {'':34}    {row['old_colour']!r} -> {row['new_colour']!r}")
    apply_plan(client, plan, testrun=testrun)
    return plan


if __name__ == "__main__":
    main(testrun="--apply" not in sys.argv)
