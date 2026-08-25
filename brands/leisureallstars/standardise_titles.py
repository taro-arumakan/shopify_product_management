"""Bring every live EPOKHE product onto the canonical colour codebook.

The catalogue grew three abbreviations for the same colour -- BLACK appears as
B, BK and BLK -- and a single initial cannot separate BLACK from BROWN, BRONZE
or BLUE. :data:`EpokheClient.COLOUR_CODES` fixes one code per colour word;
this script applies it to the products already on the store.

Handles are deliberately left alone, so product URLs do not move. The
``global.title_tag`` metafield embeds the title and is updated alongside it.

    python -m brands.leisureallstars.standardise_titles          # report only
    python -m brands.leisureallstars.standardise_titles --apply  # write
"""

import logging
import re
import sys

import utils
from brands.leisureallstars.client import COLOUR_CODES, to_shopify_product_title

logger = logging.getLogger(__name__)

VENDOR = "EPOKHE"

#: A style name that carries a colour word only to disambiguate a title the old
#: scheme could not separate. The codebook does that job now, so the word is
#: redundant -- "DYLAN Cola CP/B" becomes "DYLAN COLP/BRN", not
#: "DYLAN Cola COLP/BRN". ("DYLAN ZERO" is a real style name and stays.)
STYLE_OVERRIDES = {"DYLAN Cola": "DYLAN"}
#: Live titles end in the colour code; everything before it is the style.
CODE_PATTERN = re.compile(
    r"^(?P<style>.+?)\s+(?P<code>[A-Za-z0-9]+(?:/[A-Za-z0-9]+)*)$"
)


def split_title(title):
    """``"ANTEKA 2.0 TP/GP"`` -> ``("ANTEKA 2.0", "TP/GP")``, else (title, None)."""
    match = CODE_PATTERN.match(title.strip())
    if not match:
        return title.strip(), None
    return match.group("style"), match.group("code")


def build_plan(client):
    """One row per live product: (product, style, old_title, new_title, colour)."""
    plan = []
    for product in client.products_by_query(f"vendor:'{VENDOR}'"):
        variants = product["variants"]["nodes"]
        if not variants:
            logger.warning(f"{product['title']} has no variants, skipping")
            continue
        colour = variants[0]["title"]
        style, _code = split_title(product["title"])
        style = STYLE_OVERRIDES.get(style, style)
        plan.append(
            {
                "id": product["id"],
                "handle": product["handle"],
                "style": style,
                "colour": colour,
                "old_title": product["title"],
                "new_title": to_shopify_product_title(style, colour),
            }
        )
    return plan


def anomalies(plan):
    """Rows worth a human glance before anything is written."""
    out = {"duplicate_new_title": {}, "colour_word_in_style": [], "no_change": []}
    seen = {}
    for row in plan:
        seen.setdefault(row["new_title"], []).append(row["handle"])
        # A style like "DYLAN Cola" carries a colour word as a disambiguator,
        # which the codebook now makes redundant.
        style_words = {w.upper().strip(",-") for w in row["style"].split()}
        if style_words & set(COLOUR_CODES):
            out["colour_word_in_style"].append(row)
        if row["old_title"] == row["new_title"]:
            out["no_change"].append(row)
    out["duplicate_new_title"] = {t: h for t, h in seen.items() if len(h) > 1}
    return out


def apply_plan(client, plan, testrun=True):
    for row in plan:
        if row["old_title"] == row["new_title"]:
            continue
        seo = f"{row['new_title']} - {row['colour']}"
        if testrun:
            logger.info(f"would retitle {row['old_title']!r} -> {row['new_title']!r}")
            continue
        client.update_product_title(row["id"], row["new_title"])
        client.update_product_metafield(row["id"], "global", "title_tag", seo)
        logger.info(f"retitled {row['old_title']!r} -> {row['new_title']!r}")


def main(testrun=True):
    logging.basicConfig(level=logging.INFO)
    client = utils.client("leisureallstars")
    plan = build_plan(client)
    found = anomalies(plan)

    print(f"live {VENDOR} products : {len(plan)}")
    print(f"already correct       : {len(found['no_change'])}")
    print(f"to retitle            : {len(plan) - len(found['no_change'])}")
    if found["duplicate_new_title"]:
        print("\n*** these would end up sharing a title ***")
        for title, handles in found["duplicate_new_title"].items():
            print(f"    {title:28} {handles}")
    if found["colour_word_in_style"]:
        print("\nstyle names containing a colour word (the code now repeats it):")
        for row in found["colour_word_in_style"]:
            print(f"    {row['old_title']:26} -> {row['new_title']}")
    apply_plan(client, plan, testrun=testrun)
    return plan


if __name__ == "__main__":
    main(testrun="--apply" not in sys.argv)
