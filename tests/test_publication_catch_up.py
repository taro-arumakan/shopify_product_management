import datetime
import unittest

from helpers.publication_catch_up import (
    catch_up_other_channels,
    online_store_is_live,
    other_channels,
    unpublish_other_channels,
)

NOW = datetime.datetime(2026, 10, 14, 12, 0, tzinfo=datetime.timezone.utc)

ONLINE_STORE = {"id": "gid://shopify/Publication/1", "name": "Online Store"}
POS = {"id": "gid://shopify/Publication/2", "name": "Point of Sale"}
SHOP = {"id": "gid://shopify/Publication/3", "name": "Shop"}
GOOGLE = {"id": "gid://shopify/Publication/4", "name": "Google & YouTube"}


def state(publication, is_published, publish_date=None):
    return {
        "publication": publication,
        "isPublished": is_published,
        "publishDate": publish_date,
    }


class FakeClient:
    def __init__(self, products, states_by_id):
        self.products = products
        self.states_by_id = states_by_id
        self.published = []
        self.unpublished = []

    def products_by_tag(self, tag):
        return self.products

    def product_publication_states(self, product_id):
        return self.states_by_id[product_id]

    def publish_by_product_or_collection_id_and_publication_id(
        self, product_or_collection_id, publication_id
    ):
        self.published.append((product_or_collection_id, publication_id))

    def unpublish_by_product_or_collection_id_and_publication_id(
        self, product_or_collection_id, publication_id
    ):
        self.unpublished.append((product_or_collection_id, publication_id))


def client_for(states, product_id="gid://shopify/Product/1", title="JACKET"):
    return FakeClient(
        products=[{"id": product_id, "title": title}],
        states_by_id={product_id: states},
    )


class TestOnlineStoreIsLive(unittest.TestCase):
    def test_live_when_published_with_a_past_date(self):
        past = "2026-10-14T02:00:00Z"
        live, reason = online_store_is_live([state(ONLINE_STORE, True, past)], now=NOW)
        self.assertTrue(live)
        self.assertEqual(reason, "")

    def test_live_when_published_with_no_date(self):
        live, _ = online_store_is_live([state(ONLINE_STORE, True)], now=NOW)
        self.assertTrue(live)

    def test_not_live_while_the_publish_date_is_in_the_future(self):
        future = "2026-10-20T03:00:00Z"
        live, reason = online_store_is_live(
            [state(ONLINE_STORE, False, future)], now=NOW
        )
        self.assertFalse(live)
        self.assertIn("scheduled for", reason)

    def test_not_live_when_a_future_date_claims_to_be_published(self):
        # Belt and braces: the date wins over isPublished either way round.
        future = "2026-10-20T03:00:00Z"
        live, _ = online_store_is_live([state(ONLINE_STORE, True, future)], now=NOW)
        self.assertFalse(live)

    def test_not_live_when_unpublished_without_a_date(self):
        live, reason = online_store_is_live([state(ONLINE_STORE, False)], now=NOW)
        self.assertFalse(live)
        self.assertIn("not live yet", reason)

    def test_not_live_when_absent(self):
        live, reason = online_store_is_live([state(SHOP, True)], now=NOW)
        self.assertFalse(live)
        self.assertIn("not on the Online Store", reason)


class TestOtherChannels(unittest.TestCase):
    STATES = [
        state(ONLINE_STORE, True),
        state(POS, False),
        state(SHOP, True),
    ]

    def test_excludes_the_online_store_either_way(self):
        self.assertEqual(other_channels(self.STATES, published=False), [POS])
        self.assertEqual(other_channels(self.STATES, published=True), [SHOP])


class TestCatchUpOtherChannels(unittest.TestCase):
    def test_publishes_the_pending_channels_once_the_store_is_live(self):
        client = client_for(
            [
                state(ONLINE_STORE, True, "2026-10-14T02:00:00Z"),
                state(SHOP, False),
                state(GOOGLE, False),
            ]
        )
        res = catch_up_other_channels("asheis", "26_oct_1", client=client, now=NOW)
        self.assertEqual(
            client.published,
            [
                ("gid://shopify/Product/1", SHOP["id"]),
                ("gid://shopify/Product/1", GOOGLE["id"]),
            ],
        )
        self.assertEqual(res["published"], {"JACKET": ["Shop", "Google & YouTube"]})

    def test_never_publishes_the_online_store_itself(self):
        client = client_for(
            [state(ONLINE_STORE, False, "2026-10-20T03:00:00Z"), state(SHOP, False)]
        )
        with self.assertRaises(RuntimeError) as ctx:
            catch_up_other_channels("asheis", "26_oct_1", client=client, now=NOW)
        self.assertIn("every product was skipped", str(ctx.exception))
        self.assertEqual(client.published, [])

    def test_a_dry_run_publishes_nothing(self):
        client = client_for([state(ONLINE_STORE, True), state(SHOP, False)])
        res = catch_up_other_channels(
            "asheis", "26_oct_1", dry_run=True, client=client, now=NOW
        )
        self.assertEqual(client.published, [])
        self.assertEqual(res["published"], {"JACKET": ["Shop"]})

    def test_re_running_after_a_catch_up_is_a_no_op(self):
        client = client_for([state(ONLINE_STORE, True), state(SHOP, True)])
        res = catch_up_other_channels("asheis", "26_oct_1", client=client, now=NOW)
        self.assertEqual(client.published, [])
        self.assertEqual(res["up_to_date"], ["JACKET"])
        self.assertEqual(res["skipped"], {})

    def test_a_partial_skip_still_publishes_the_rest(self):
        client = FakeClient(
            products=[
                {"id": "gid://shopify/Product/1", "title": "LIVE"},
                {"id": "gid://shopify/Product/2", "title": "SCHEDULED"},
            ],
            states_by_id={
                "gid://shopify/Product/1": [
                    state(ONLINE_STORE, True),
                    state(SHOP, False),
                ],
                "gid://shopify/Product/2": [
                    state(ONLINE_STORE, False, "2026-10-20T03:00:00Z"),
                    state(SHOP, False),
                ],
            },
        )
        res = catch_up_other_channels("asheis", "26_oct_1", client=client, now=NOW)
        self.assertEqual(client.published, [("gid://shopify/Product/1", SHOP["id"])])
        self.assertEqual(list(res["published"]), ["LIVE"])
        self.assertEqual(list(res["skipped"]), ["SCHEDULED"])

    def test_an_unknown_tag_fails_loudly(self):
        client = FakeClient(products=[], states_by_id={})
        with self.assertRaises(RuntimeError) as ctx:
            catch_up_other_channels("asheis", "nope", client=client, now=NOW)
        self.assertIn("no products tagged", str(ctx.exception))


class TestUnpublishOtherChannels(unittest.TestCase):
    def test_removes_the_live_other_channels_only(self):
        client = client_for(
            [
                state(ONLINE_STORE, True),
                state(SHOP, True),
                state(GOOGLE, True),
                state(POS, False),
            ]
        )
        res = unpublish_other_channels("asheis", "26_oct_1", client=client)
        self.assertEqual(
            client.unpublished,
            [
                ("gid://shopify/Product/1", SHOP["id"]),
                ("gid://shopify/Product/1", GOOGLE["id"]),
            ],
        )
        self.assertEqual(res, {"JACKET": ["Shop", "Google & YouTube"]})

    def test_leaves_a_scheduled_online_store_publication_alone(self):
        client = client_for(
            [state(ONLINE_STORE, False, "2026-10-20T03:00:00Z"), state(SHOP, True)]
        )
        unpublish_other_channels("asheis", "26_oct_1", client=client)
        self.assertEqual(client.unpublished, [("gid://shopify/Product/1", SHOP["id"])])

    def test_nothing_to_do(self):
        client = client_for([state(ONLINE_STORE, True), state(SHOP, False)])
        self.assertEqual(
            unpublish_other_channels("asheis", "26_oct_1", client=client), {}
        )
        self.assertEqual(client.unpublished, [])

    def test_a_dry_run_unpublishes_nothing(self):
        client = client_for([state(ONLINE_STORE, True), state(SHOP, True)])
        res = unpublish_other_channels(
            "asheis", "26_oct_1", dry_run=True, client=client
        )
        self.assertEqual(client.unpublished, [])
        self.assertEqual(res, {"JACKET": ["Shop"]})


if __name__ == "__main__":
    unittest.main()
