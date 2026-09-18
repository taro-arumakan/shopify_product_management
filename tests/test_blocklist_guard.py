import os
import unittest
from unittest.mock import patch

from brands.lememe.blocklist_guard import (
    BlocklistGuard,
    _house_numbers,
    _norm_phone,
    build_blocklist,
    evaluate_order,
)
from helpers.shopify_graphql_client.client import ShopifyGraphqlClient

SOURCE = {
    "id": "gid://shopify/Order/1273",
    "name": "#LM-1273",
    "tags": ["blocklist"],
    "email": "Buyer@Example.com",
    "phone": None,
    "customer": {
        "id": "gid://shopify/Customer/1",
        "defaultEmailAddress": {"emailAddress": "buyer@example.com"},
        "defaultPhoneNumber": None,
        "addressesV2": {"nodes": []},
    },
    "shippingAddress": {
        "address1": "桜町1丁目2番3号",
        "address2": "サクラハイツ101",
        "zip": "150-0001",
        "phone": "090-1234-5678",
    },
    "billingAddress": None,
}


def make_order(
    ship=None,
    bill=None,
    email="someone@example.com",
    phone=None,
    customer_id="gid://shopify/Customer/2",
    tags=None,
    name="#TEST",
    source_name="web",
):
    return {
        "id": "gid://shopify/Order/9",
        "name": name,
        "tags": tags or [],
        "sourceName": source_name,
        "email": email,
        "phone": phone,
        "customer": {"id": customer_id} if customer_id else None,
        "shippingAddress": ship,
        "billingAddress": bill,
    }


def other_address():
    return {"address1": "青葉5-6-7", "zip": "980-0001", "phone": "0311112222"}


class TestNormalization(unittest.TestCase):
    def test_house_numbers_in_any_notation(self):
        expected = (1, 2, 3, 101)
        self.assertEqual(_house_numbers("桜町1丁目2番3号", "サクラハイツ101"), expected)
        self.assertEqual(
            _house_numbers("桜町１－２－３", "サクラハイツ１０１"), expected
        )
        self.assertEqual(_house_numbers("桜町一丁目2-3 サクラハイツ101号室"), expected)
        self.assertEqual(_house_numbers("桜町1の2の3", "101"), expected)

    def test_kanji_chome_above_ten(self):
        self.assertEqual(_house_numbers("本町十二丁目5"), (12, 5))
        self.assertEqual(_house_numbers("本町二十丁目5"), (20, 5))

    def test_phone_folds_country_code(self):
        self.assertEqual(_norm_phone("+81 90-1234-5678"), "09012345678")
        self.assertEqual(_norm_phone("０９０（１２３４）５６７８"), "09012345678")
        self.assertEqual(_norm_phone("+81 3-1234-5678"), "0312345678")
        self.assertIsNone(_norm_phone("123"))
        self.assertIsNone(_norm_phone(None))


class TestEvaluateOrder(unittest.TestCase):
    def setUp(self):
        self.blocklist = build_blocklist([SOURCE])

    def test_same_customer_record(self):
        ev = evaluate_order(
            make_order(ship=other_address(), customer_id="gid://shopify/Customer/1"),
            self.blocklist,
        )
        self.assertTrue(ev["is_blocked"])
        self.assertEqual(ev["matches"], {"customer record": "#LM-1273"})

    def test_guest_with_same_email_different_case(self):
        ev = evaluate_order(
            make_order(ship=other_address(), email=" BUYER@example.com "),
            self.blocklist,
        )
        self.assertEqual(ev["matches"], {"e-mail": "#LM-1273"})

    def test_new_email_same_phone_on_shipping_address(self):
        ship = {**other_address(), "phone": "+819012345678"}
        ev = evaluate_order(make_order(ship=ship), self.blocklist)
        self.assertEqual(ev["matches"], {"phone": "#LM-1273"})

    def test_same_address_written_differently_without_building(self):
        ship = {"address1": "桜町１－２－３", "zip": "１５０－０００１"}
        ev = evaluate_order(make_order(ship=ship), self.blocklist)
        self.assertEqual(ev["matches"], {"shipping address": "#LM-1273"})

    def test_billing_address_alone_matches(self):
        bill = {"address1": "桜町1-2-3", "address2": "101", "zip": "1500001"}
        ev = evaluate_order(make_order(ship=other_address(), bill=bill), self.blocklist)
        self.assertEqual(ev["matches"], {"billing address": "#LM-1273"})

    def test_other_room_in_same_building_not_flagged(self):
        ship = {
            "address1": "桜町1-2-3",
            "address2": "サクラハイツ102",
            "zip": "150-0001",
        }
        ev = evaluate_order(make_order(ship=ship), self.blocklist)
        self.assertFalse(ev["is_blocked"])

    def test_same_numbers_other_postcode_not_flagged(self):
        ship = {"address1": "青葉1-2-3", "address2": "101", "zip": "980-0001"}
        ev = evaluate_order(make_order(ship=ship), self.blocklist)
        self.assertFalse(ev["is_blocked"])

    def test_same_postcode_without_numbers_not_flagged(self):
        ship = {"address1": "桜町", "zip": "150-0001"}
        ev = evaluate_order(make_order(ship=ship), self.blocklist)
        self.assertFalse(ev["is_blocked"])

    def test_saved_customer_address_is_blocklisted_too(self):
        source = {
            **SOURCE,
            "customer": {
                **SOURCE["customer"],
                "addressesV2": {"nodes": [{"address1": "緑町4-5", "zip": "460-0002"}]},
            },
        }
        ship = {"address1": "緑町4-5", "zip": "460-0002"}
        ev = evaluate_order(make_order(ship=ship), build_blocklist([source]))
        self.assertEqual(ev["matches"], {"shipping address": "#LM-1273"})

    def test_unrelated_order_not_flagged(self):
        ev = evaluate_order(make_order(ship=other_address()), self.blocklist)
        self.assertFalse(ev["is_blocked"])
        self.assertEqual(ev["reasons"], [])

    def test_missing_everything(self):
        ev = evaluate_order(
            {"shippingAddress": None, "billingAddress": None, "customer": None},
            self.blocklist,
        )
        self.assertFalse(ev["is_blocked"])


def orders_page(nodes):
    return {
        "orders": {
            "pageInfo": {"hasNextPage": False, "endCursor": None},
            "nodes": nodes,
        }
    }


def fake_run_query(scan_nodes, sources=(SOURCE,)):
    """First call fetches the blocklist sources, the rest the orders to scan."""

    def run_query(query, variables=None):
        if variables["q"] == "tag:'blocklist'":
            return orders_page(list(sources))
        return orders_page(scan_nodes)

    return run_query


BLOCKED_SHIP = {"address1": "桜町1-2-3", "address2": "101", "zip": "150-0001"}


@patch.dict(os.environ, {"NOTIFYEES_LEMEME_ORDER_GUARDS": "ops@example.com"})
@patch("helpers.client.send_smtp_email")
@patch.object(ShopifyGraphqlClient, "fulfillment_order_hold")
@patch.object(
    ShopifyGraphqlClient,
    "order_fulfillment_orders",
    return_value=[{"id": "gid://shopify/FulfillmentOrder/5", "status": "OPEN"}],
)
@patch.object(ShopifyGraphqlClient, "order_add_tags")
@patch.object(ShopifyGraphqlClient, "run_query")
class TestBlocklistGuardScan(unittest.TestCase):
    def guard(self):
        return BlocklistGuard(
            client=ShopifyGraphqlClient(shop_name="lememek", access_token="dummy")
        )

    def test_live_scan_holds_tags_and_notifies_matches_only(
        self, run_query, add_tags, fulfillment_orders, hold, send_email
    ):
        run_query.side_effect = fake_run_query(
            [
                make_order(ship=BLOCKED_SHIP, name="#A"),
                make_order(ship=other_address(), name="#B"),
            ]
        )
        matched = self.guard().scan(dry_run=False)

        self.assertEqual([m[0]["name"] for m in matched], ["#A"])
        add_tags.assert_called_once_with("gid://shopify/Order/9", ["blocklist-review"])
        hold.assert_called_once()
        self.assertEqual(hold.call_args[0][0], "gid://shopify/FulfillmentOrder/5")
        self.assertEqual(hold.call_args[1]["handle"], "blocklist-guard")
        self.assertIn("#LM-1273", hold.call_args[1]["reason_notes"])
        body = send_email.call_args[1]["body"]
        self.assertIn("#A", body)
        self.assertIn("held 1 fulfillment order(s)", body)
        self.assertIn("https://admin.shopify.com/store/lememek/orders/9", body)
        self.assertNotIn("BY HAND", body)

    def test_dry_run_changes_nothing(
        self, run_query, add_tags, fulfillment_orders, hold, send_email
    ):
        run_query.side_effect = fake_run_query([make_order(ship=BLOCKED_SHIP)])
        matched = self.guard().scan(dry_run=True)

        self.assertEqual(len(matched), 1)
        add_tags.assert_not_called()
        hold.assert_not_called()
        send_email.assert_not_called()

    def test_skips_the_incident_itself_and_draft_orders(
        self, run_query, add_tags, fulfillment_orders, hold, send_email
    ):
        run_query.side_effect = fake_run_query(
            [
                make_order(ship=BLOCKED_SHIP, tags=["blocklist"], name="#LM-1273"),
                make_order(
                    ship=BLOCKED_SHIP, source_name="shopify_draft_order", name="#D"
                ),
            ]
        )
        self.assertEqual(self.guard().scan(dry_run=False), [])
        add_tags.assert_not_called()
        hold.assert_not_called()

    def test_does_not_renotify_already_tagged_order(
        self, run_query, add_tags, fulfillment_orders, hold, send_email
    ):
        run_query.side_effect = fake_run_query(
            [make_order(ship=BLOCKED_SHIP, tags=["blocklist-review"])]
        )
        matched = self.guard().scan(dry_run=False)

        self.assertEqual(len(matched), 1)
        add_tags.assert_not_called()
        hold.assert_not_called()
        send_email.assert_not_called()

    def test_no_blocklist_scans_nothing(
        self, run_query, add_tags, fulfillment_orders, hold, send_email
    ):
        run_query.side_effect = fake_run_query(
            [make_order(ship=BLOCKED_SHIP)], sources=()
        )
        self.assertEqual(self.guard().scan(dry_run=False), [])
        run_query.assert_called_once()  # the blocklist lookup only

    def test_failed_hold_is_tagged_and_reported(
        self, run_query, add_tags, fulfillment_orders, hold, send_email
    ):
        run_query.side_effect = fake_run_query([make_order(ship=BLOCKED_SHIP)])
        hold.side_effect = RuntimeError("cannot hold")
        self.guard().scan(dry_run=False)

        add_tags.assert_called_once()
        body = send_email.call_args[1]["body"]
        self.assertIn("HOLD FAILED (cannot hold)", body)
        self.assertIn("STOP THE SHIPMENT BY HAND", body)

    def test_partly_shipped_order_is_reported_for_manual_stop(
        self, run_query, add_tags, fulfillment_orders, hold, send_email
    ):
        run_query.side_effect = fake_run_query([make_order(ship=BLOCKED_SHIP)])
        fulfillment_orders.return_value = [
            {"id": "gid://shopify/FulfillmentOrder/5", "status": "IN_PROGRESS"}
        ]
        self.guard().scan(dry_run=False)

        hold.assert_not_called()
        body = send_email.call_args[1]["body"]
        self.assertIn("left as is: IN_PROGRESS", body)
        self.assertIn("STOP THE SHIPMENT BY HAND", body)

    def test_failed_tagging_leaves_order_for_next_run(
        self, run_query, add_tags, fulfillment_orders, hold, send_email
    ):
        run_query.side_effect = fake_run_query([make_order(ship=BLOCKED_SHIP)])
        add_tags.side_effect = RuntimeError("tagsAdd failed")
        self.guard().scan(dry_run=False)
        send_email.assert_not_called()

    def test_live_scan_needs_recipients_before_touching_orders(
        self, run_query, add_tags, fulfillment_orders, hold, send_email
    ):
        run_query.side_effect = fake_run_query([make_order(ship=BLOCKED_SHIP)])
        with patch.dict(os.environ, {"NOTIFYEES_LEMEME_ORDER_GUARDS": ""}):
            with self.assertRaises(RuntimeError):
                self.guard().scan(dry_run=False)
        run_query.assert_not_called()
        hold.assert_not_called()


if __name__ == "__main__":
    unittest.main()
