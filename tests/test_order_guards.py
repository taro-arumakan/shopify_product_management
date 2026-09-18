import os
import unittest
from unittest.mock import patch

from brands.lememe.blocklist_guard import BlocklistGuard
from brands.lememe.forwarder_guard import ForwarderGuard
from brands.lememe.order_guards import recipients, run_order_guards
from helpers.shopify_graphql_client.client import ShopifyGraphqlClient


class TestRecipients(unittest.TestCase):
    def test_comma_separated(self):
        with patch.dict(
            os.environ,
            {"NOTIFYEES_LEMEME_ORDER_GUARDS": " a@example.com, b@example.com ,"},
        ):
            self.assertEqual(recipients(), ["a@example.com", "b@example.com"])

    def test_no_default(self):
        for value in ("", "  ,  "):
            with patch.dict(os.environ, {"NOTIFYEES_LEMEME_ORDER_GUARDS": value}):
                with self.assertRaises(RuntimeError) as ctx:
                    recipients()
                self.assertIn("NOTIFYEES_LEMEME_ORDER_GUARDS", str(ctx.exception))

    def test_both_guards_use_the_shared_list(self):
        with patch.dict(os.environ, {"NOTIFYEES_LEMEME_ORDER_GUARDS": "a@example.com"}):
            self.assertEqual(BlocklistGuard._recipients(), ["a@example.com"])
            self.assertEqual(ForwarderGuard._recipients(), ["a@example.com"])


class TestRunOrderGuards(unittest.TestCase):
    def setUp(self):
        self.client = ShopifyGraphqlClient(shop_name="lememek", access_token="dummy")
        self.calls = []

    def recording_scan(self, name, result=None, error=None):
        test = self

        def scan(guard, **kwargs):
            test.calls.append((name, guard.client, kwargs))
            if error:
                raise error
            return result

        return scan

    def test_runs_both_on_one_client_blocklist_first(self):
        with (
            patch.object(
                BlocklistGuard, "scan", self.recording_scan("blocklist", ["b"])
            ),
            patch.object(
                ForwarderGuard, "scan", self.recording_scan("forwarder", ["f"])
            ),
        ):
            results = run_order_guards(
                dry_run=True, processed_after="2026-09-01", client=self.client
            )

        self.assertEqual(results, {"blocklist": ["b"], "forwarder": ["f"]})
        self.assertEqual([c[0] for c in self.calls], ["blocklist", "forwarder"])
        self.assertTrue(all(c[1] is self.client for c in self.calls))
        for _, _, kwargs in self.calls:
            self.assertEqual(
                kwargs,
                {
                    "processed_after": "2026-09-01",
                    "dry_run": True,
                    "max_pages": 20,
                    "active_only": True,
                },
            )

    def test_live_by_default(self):
        with (
            patch.object(BlocklistGuard, "scan", self.recording_scan("blocklist")),
            patch.object(ForwarderGuard, "scan", self.recording_scan("forwarder")),
        ):
            run_order_guards(client=self.client)
        self.assertTrue(all(c[2]["dry_run"] is False for c in self.calls))

    def test_one_failing_guard_does_not_stop_the_other(self):
        with (
            patch.object(
                BlocklistGuard,
                "scan",
                self.recording_scan("blocklist", error=ValueError()),
            ),
            patch.object(ForwarderGuard, "scan", self.recording_scan("forwarder", [])),
        ):
            with self.assertRaises(RuntimeError) as ctx:
                run_order_guards(client=self.client)

        self.assertEqual([c[0] for c in self.calls], ["blocklist", "forwarder"])
        self.assertIn("blocklist", str(ctx.exception))
        self.assertNotIn("forwarder", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
