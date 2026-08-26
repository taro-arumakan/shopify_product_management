"""Create the missing style collections for the SOH260818 batch.

Every EPOKHE style has a collection automated on ``TAG EQUALS <STYLE>``, and
each product points at its own with ``custom.product_collection`` -- that is
what the ``product-with-collection`` template reads to show the rest of the
style on a product page. Twelve of the nineteen styles in this batch have no
collection yet, so without this their products would render without it.

New collections copy REALM, the most recent one the owner created for a style
not yet on the store: sorted BEST_SELLING, no template suffix, no image and no
description. Image and template are merchandising and are left to the owner --
24 of the 32 existing style collections have an image, 29 use the
``with-a-highlight-product`` template.

Collaborations do not get their own collection: GUILTY x Thomas Townend is
tagged GUILTY and belongs in the GUILTY collection.

    python -m brands.leisureallstars.create_style_collections          # report
    python -m brands.leisureallstars.create_style_collections --apply  # write
"""

import logging
import sys

from brands.leisureallstars import image_mapping
from brands.leisureallstars.product_create import SHEET_NAME, build_client

logger = logging.getLogger(__name__)

COLLECTION_CREATE = """
mutation createCollection($input: CollectionInput!) {
    collectionCreate(input: $input) {
        collection { id title handle sortOrder ruleSet { rules { column relation condition } } }
        userErrors { field message }
    }
}
"""


def missing_styles(client):
    """``{style tag: [sku, ...]}`` for every new style with no collection."""
    new_skus = set(image_mapping.SKU_IMAGE_SOURCE)
    wanted = {}
    for product_input in client.product_inputs_by_sheet_name(SHEET_NAME):
        if product_input["sku"] not in new_skus:
            continue
        wanted.setdefault(client.style_tag(product_input["style"]), []).append(
            product_input["sku"]
        )
    return {
        style: skus
        for style, skus in sorted(wanted.items())
        if not client.collection_gid_for(style)
    }


def create(client, style):
    variables = {
        "input": {
            "title": style,
            "sortOrder": "BEST_SELLING",
            "ruleSet": {
                "appliedDisjunctively": False,
                "rules": [{"column": "TAG", "relation": "EQUALS", "condition": style}],
            },
        }
    }
    return client.collection_create_by_query_and_publish(COLLECTION_CREATE, variables)


def main(testrun=True):
    logging.basicConfig(level=logging.INFO)
    client = build_client()
    missing = missing_styles(client)
    print(f"styles with no collection: {len(missing)}")
    for style, skus in missing.items():
        print(f"    {style:<32} {len(skus)} product(s)")
    for style in missing:
        if testrun:
            logger.info(f"would create collection {style!r} on TAG EQUALS {style!r}")
            continue
        created = create(client, style)
        logger.info(f"created {created['title']!r} as /collections/{created['handle']}")
    return missing


if __name__ == "__main__":
    main(testrun="--apply" not in sys.argv)
