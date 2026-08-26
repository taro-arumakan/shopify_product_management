"""Give every live EPOKHE product the two metafields its siblings carry.

``global.title_tag`` is the SEO title (it backs ``product.seo.title``) and
``custom.product_collection`` is what the ``product-with-collection`` template
reads to show the rest of the style. All 143 EPOKHE products predating the
SOH260818 batch have both; products created by :mod:`.product_create` before
:meth:`EpokheClient.post_process_product_input` set them do not.

A product whose style has no collection yet gets the SEO tag and a warning --
the collection has to exist before the reference can point at it, and creating
one is a merchandising decision.

    python -m brands.leisureallstars.backfill_metafields          # report only
    python -m brands.leisureallstars.backfill_metafields --apply  # write
"""

import logging
import sys

from brands.leisureallstars.client import EpokheClient

logger = logging.getLogger(__name__)


def split_title(title):
    """``"GUILTY x Thomas Townend BLKP/BRZ"`` -> the style half."""
    return title.rsplit(" ", 1)[0]


def build_plan(client):
    plan = []
    for product in client.products_by_query(f"vendor:'{client.VENDOR}'"):
        variants = product["variants"]["nodes"]
        if not variants:
            continue
        present = {
            m["namespace"] + "." + m["key"] for m in product["metafields"]["nodes"]
        }
        missing = [
            spec
            for spec in (client.SEO_METAFIELD, client.COLLECTION_METAFIELD)
            if f"{spec[0]}.{spec[1]}" not in present
        ]
        if not missing:
            continue
        plan.append(
            {
                "id": product["id"],
                "title": product["title"],
                "colour": variants[0]["title"],
                "style": split_title(product["title"]),
                "missing": missing,
            }
        )
    return plan


def metafields_for(client, row):
    out = []
    for namespace, key, kind in row["missing"]:
        if key == "title_tag":
            value = client.seo_title(row["title"], row["colour"])
        else:
            value = client.collection_gid_for(row["style"])
            if not value:
                continue
        out.append(dict(namespace=namespace, key=key, type=kind, value=value))
    return out


def apply_plan(client, plan, testrun=True):
    for row in plan:
        metafields = metafields_for(client, row)
        if not metafields:
            continue
        keys = [m["key"] for m in metafields]
        if testrun:
            logger.info(f"would set {keys} on {row['title']}")
            continue
        client.metafields_set(row["id"], metafields)
        logger.info(f"set {keys} on {row['title']}")


def main(testrun=True):
    logging.basicConfig(level=logging.INFO)
    client = EpokheClient()
    plan = build_plan(client)
    print(f"products missing a metafield: {len(plan)}")
    for row in plan:
        print(f"    {row['title']:26} missing {[m[1] for m in row['missing']]}")
    apply_plan(client, plan, testrun=testrun)
    return plan


if __name__ == "__main__":
    main(testrun="--apply" not in sys.argv)
