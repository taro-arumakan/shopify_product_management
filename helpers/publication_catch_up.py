"""Publish a drop to the sales channels a scheduled launch had to leave behind.

Shopify only honours `PublicationInput.publishDate` on the Online Store -
"Only online store channels support future publishing". Passing a future date
to Shop, Google & YouTube or Facebook & Instagram does not schedule anything,
it publishes immediately, which puts the drop in front of shoppers days before
the store launch. So `publish_by_product_or_collection_id` publishes only the
Online Store whenever a scheduled time is given, and this module is what fills
in the rest once the launch has actually happened.

Every brand uses the same entry point. Each shop's Shopify Flow ("Scheduled
time" trigger, then "Send HTTP request" to the run_func workflow) dispatches:

    script_path  helpers/publication_catch_up.py
    func_name    catch_up_other_channels
    params       {"shop_name": "asheis", "tag": "26_oct_1"}

Schedule the Flow a little after the launch time, not on it: a product whose
Online Store publication has not flipped yet is skipped rather than published
early, and a run where every product is skipped fails so the Action goes red.
Re-running after a successful catch-up is a no-op.

`unpublish_other_channels` is the repair in the other direction, for products
that reached those channels early:

    python -m helpers.publication_catch_up --shop asheis --tag 26_oct_1
    python -m helpers.publication_catch_up --shop asheis --tag 26_oct_1 --apply
    python -m helpers.publication_catch_up --shop asheis --tag 26_oct_1 --unpublish --apply
"""

import datetime
import logging

from helpers.shopify_graphql_client.publications import ONLINE_STORE

logger = logging.getLogger(__name__)


def _parse_publish_date(value):
    if not value:
        return None
    # Shopify returns ISO 8601 with a Z suffix.
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))


def online_store_is_live(states, now=None):
    """Has the Online Store launch already happened for this product?

    Returns (True, "") once it has, and (False, reason) while it has not, so
    the caller can log why a product was left alone.
    """
    now = now or datetime.datetime.now(datetime.timezone.utc)
    state = next((s for s in states if s["publication"]["name"] == ONLINE_STORE), None)
    if state is None:
        return False, f"not on the {ONLINE_STORE} at all"
    publish_date = _parse_publish_date(state.get("publishDate"))
    if publish_date and publish_date > now:
        return False, f"{ONLINE_STORE} publish scheduled for {publish_date}"
    if not state["isPublished"]:
        return False, f"{ONLINE_STORE} publication is not live yet"
    return True, ""


def other_channels(states, published):
    """Publications besides the Online Store, filtered by publish state."""
    return [
        s["publication"]
        for s in states
        if s["publication"]["name"] != ONLINE_STORE and s["isPublished"] is published
    ]


def _products(client, shop_name, tag):
    products = client.products_by_tag(tag)
    if not products:
        raise RuntimeError(f"no products tagged {tag!r} in {shop_name}")
    logger.info(f"{len(products)} product(s) tagged {tag!r} in {shop_name}")
    return products


def _client(shop_name, client=None):
    if client:
        return client
    import utils

    return utils.client(shop_name)


def catch_up_other_channels(shop_name, tag, dry_run=False, client=None, now=None):
    """Publish tagged products to every channel their scheduled launch skipped.

    Products whose Online Store launch has not happened yet are left alone -
    publishing them now is the very thing this is meant to prevent.
    """
    logging.basicConfig(level=logging.INFO)
    client = _client(shop_name, client)
    published, skipped, up_to_date = {}, {}, []

    for product in _products(client, shop_name, tag):
        title = product["title"]
        states = client.product_publication_states(product["id"])
        live, reason = online_store_is_live(states, now=now)
        if not live:
            logger.warning(f"skipping {title}: {reason}")
            skipped[title] = reason
            continue
        pending = other_channels(states, published=False)
        if not pending:
            logger.info(f"{title} is already on every channel")
            up_to_date.append(title)
            continue
        names = [p["name"] for p in pending]
        logger.info(
            f"{'would publish' if dry_run else 'publishing'} {title} to "
            f"{', '.join(names)}"
        )
        if not dry_run:
            for publication in pending:
                client.publish_by_product_or_collection_id_and_publication_id(
                    product_or_collection_id=product["id"],
                    publication_id=publication["id"],
                )
        published[title] = names

    logger.info(
        f"catch-up {'(dry run) ' if dry_run else ''}done: "
        f"{len(published)} published, {len(up_to_date)} already current, "
        f"{len(skipped)} skipped"
    )
    if skipped and not published:
        # A Flow that fired before the launch would otherwise pass silently and
        # leave the drop off every channel but the store.
        raise RuntimeError(
            f"nothing to catch up for {tag!r}: every product was skipped - "
            f"{skipped}"
        )
    return {"published": published, "up_to_date": up_to_date, "skipped": skipped}


def unpublish_other_channels(shop_name, tag, dry_run=False, client=None):
    """Take tagged products back off every channel but the Online Store.

    The repair for products published to Shop / Google / Meta ahead of their
    launch. The Online Store publication, scheduled or live, is never touched.
    """
    logging.basicConfig(level=logging.INFO)
    client = _client(shop_name, client)
    unpublished = {}

    for product in _products(client, shop_name, tag):
        title = product["title"]
        states = client.product_publication_states(product["id"])
        live = other_channels(states, published=True)
        if not live:
            logger.info(f"{title} is on no channel but the {ONLINE_STORE}")
            continue
        names = [p["name"] for p in live]
        logger.info(
            f"{'would unpublish' if dry_run else 'unpublishing'} {title} from "
            f"{', '.join(names)}"
        )
        if not dry_run:
            # By publication id, not name: product_publication_states already
            # carries the ids, and the name-based call would re-query every
            # publication (which lists 250 products each) per product.
            for publication in live:
                client.unpublish_by_product_or_collection_id_and_publication_id(
                    product_or_collection_id=product["id"],
                    publication_id=publication["id"],
                )
        unpublished[title] = names

    logger.info(
        f"unpublish {'(dry run) ' if dry_run else ''}done: "
        f"{len(unpublished)} product(s) taken off other channels"
    )
    return unpublished


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--shop", required=True, help="Shop name, e.g. asheis.")
    parser.add_argument("--tag", required=True, help="Drop tag, e.g. 26_oct_1.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually publish / unpublish (default: dry-run, read-only).",
    )
    parser.add_argument(
        "--unpublish",
        action="store_true",
        help="Take the products off the other channels instead of publishing them.",
    )
    args = parser.parse_args()

    func = unpublish_other_channels if args.unpublish else catch_up_other_channels
    func(shop_name=args.shop, tag=args.tag, dry_run=not args.apply)


if __name__ == "__main__":
    # main()
    unpublish_other_channels(shop_name="asheis", tag="26_oct_1", dry_run=False)
    unpublish_other_channels(shop_name="asheis", tag="26_oct_2", dry_run=False)
