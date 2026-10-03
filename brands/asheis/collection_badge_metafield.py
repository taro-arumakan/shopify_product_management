"""Create and set custom.hide_launch_badge on ASHEIS collections.

snippets/product-badges.liquid renders a COMING SOON badge on every card whose
product is still behind custom.launch_datetime (set by launch_gate.py). On a
collection that is ENTIRELY pre-launch that badge lands on every card and carries
no information, so the theme reads this boolean off the collection and suppresses
it there, while leaving it on mixed collections such as /collections/all.

Carried as a collection metafield rather than as a `collection.coming-soon`
template suffix on purpose: duplicating a collection template also duplicates
every section setting inside it, and the two copies drift apart the first time
someone edits the product grid on one of them. One boolean does not justify that.

Two things the theme side depends on:
  - The flag is only read for product CARDS, so the product page keeps its badge
    even when the shopper arrived via a suppressed collection.
  - Unset means "show". New collections therefore need no action here, and the
    badge keeps working everywhere it is useful.

Suppressing the badge does NOT bring back the SOLD OUT badge: that is suppressed
off custom.launch_datetime directly, not off the presence of this badge.

    PYTHONPATH=. uv run python -c "from brands.asheis.collection_badge_metafield import *; create_definition()"
    PYTHONPATH=. uv run python -c "from brands.asheis.collection_badge_metafield import *; create_definition(dry_run=False)"
    PYTHONPATH=. uv run python -c "from brands.asheis.collection_badge_metafield import *; set_flag('coming-soon', dry_run=False)"
"""

import logging

import utils

logger = logging.getLogger(__name__)

NAMESPACE = "custom"
KEY = "hide_launch_badge"
OWNER_TYPE = "COLLECTION"

NAME = "Hide COMING SOON badge"
DESCRIPTION = (
    "Hide the COMING SOON badge on this collection's product cards. "
    "For collections where every product is a pre-launch drop, so the badge "
    "would appear on every card and say nothing. Leave off elsewhere."
)

# PUBLIC_READ is what lets Liquid read the value as
# collection.metafields.custom.hide_launch_badge.value.
DEFINITION = {
    "name": NAME,
    "namespace": NAMESPACE,
    "key": KEY,
    "description": DESCRIPTION,
    "type": "boolean",
    "ownerType": OWNER_TYPE,
    "pin": True,
    "access": {"storefront": "PUBLIC_READ"},
}

EXISTING_QUERY = """
query($namespace: String!, $key: String!, $ownerType: MetafieldOwnerType!) {
  metafieldDefinitions(first: 10, namespace: $namespace, key: $key, ownerType: $ownerType) {
    nodes { id name namespace key pinnedPosition type { name } }
  }
}
"""

CREATE_MUTATION = """
mutation($definition: MetafieldDefinitionInput!) {
  metafieldDefinitionCreate(definition: $definition) {
    createdDefinition { id name namespace key type { name } ownerType }
    userErrors { field message code }
  }
}
"""


def _existing(client):
    """The custom.hide_launch_badge collection definition, or None."""
    res = client.run_query(
        EXISTING_QUERY,
        {"namespace": NAMESPACE, "key": KEY, "ownerType": OWNER_TYPE},
    )
    nodes = res["metafieldDefinitions"]["nodes"]
    return nodes[0] if nodes else None


def create_definition(dry_run=True):
    """Create the collection-level boolean definition. Idempotent."""
    client = utils.client("ASHEIS")

    if found := _existing(client):
        logger.info(f"{NAMESPACE}.{KEY} already defined: {found['id']} - nothing to do")
        return found

    logger.info(
        f"{'would create' if dry_run else 'creating'} "
        f"{OWNER_TYPE.lower()} metafield definition {NAMESPACE}.{KEY} (boolean)"
    )
    if dry_run:
        return None

    res = client.run_query(CREATE_MUTATION, {"definition": DEFINITION})
    payload = res["metafieldDefinitionCreate"]
    if errors := payload["userErrors"]:
        raise RuntimeError(f"Failed to create {NAMESPACE}.{KEY}: {errors}")

    created = payload["createdDefinition"]
    logger.info(f"created {created['id']}")
    return created


def _collection_by_handle(client, handle):
    collections = client.collections_by_query(f"handle:{handle}")
    # The query is a prefix/fuzzy match, so filter to the exact handle.
    exact = [c for c in collections if c["handle"] == handle]
    if len(exact) != 1:
        raise RuntimeError(
            f"{'Multiple' if exact else 'No'} collections with handle {handle!r}: "
            f"{[c['handle'] for c in collections]}"
        )
    return exact[0]


def set_flag(handle, value=True, dry_run=True):
    """Turn the badge suppression on (or off) for one collection."""
    client = utils.client("ASHEIS")

    if not _existing(client):
        raise RuntimeError(
            f"{NAMESPACE}.{KEY} is not defined yet - run create_definition(dry_run=False) first"
        )

    collection = _collection_by_handle(client, handle)
    logger.info(
        f"{'would set' if dry_run else 'setting'} {NAMESPACE}.{KEY}="
        f"{str(value).lower()} on {collection['title']!r} ({handle})"
    )
    if dry_run:
        return None

    return client.metafields_set(
        collection["id"],
        [
            {
                "namespace": NAMESPACE,
                "key": KEY,
                "type": "boolean",
                "value": str(bool(value)).lower(),
            }
        ],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_definition()
