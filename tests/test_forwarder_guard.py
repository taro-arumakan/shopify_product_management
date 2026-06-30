import unittest
from unittest.mock import patch

from brands.lememe.forwarder_guard import evaluate_order, ForwarderGuard
from helpers.shopify_graphql_client.client import ShopifyGraphqlClient


def make_order(ship, bill_cc=None, tags=None, name="#TEST"):
    return {
        "id": "gid://shopify/Order/1",
        "name": name,
        "tags": tags or [],
        "shippingAddress": ship,
        "billingAddress": {"countryCodeV2": bill_cc} if bill_cc else None,
    }


class TestEvaluateOrder(unittest.TestCase):
    def test_buyandship_real_order_lm1258(self):
        ev = evaluate_order(
            make_order(
                {
                    "name": "Mei Kwan BSZGRXHZ Wong",
                    "firstName": "Mei Kwan BSZGRXHZ",
                    "lastName": "Wong",
                    "company": None,
                    "address1": "幸神平1 C棟01室 BSZGRXHZ",
                    "address2": None,
                    "city": "坂東市",
                    "zip": "306-0608",
                    "countryCodeV2": "JP",
                },
                bill_cc="HK",
            )
        )
        self.assertTrue(ev["is_forwarder"])
        self.assertEqual(ev["service"], "Buyandship")
        self.assertEqual(ev["confidence"], "high")
        joined = " ".join(ev["reasons"])
        self.assertIn("known forwarder hub", joined)
        self.assertIn("BSZGRXHZ", joined)
        self.assertIn("repeated in name & address", joined)
        self.assertTrue(ev["signals"]["billing_mismatch"])

    def test_hub_match_code_only_in_address(self):
        # name carries no code; caught by the denylist hub + BS prefix in address.
        ev = evaluate_order(
            make_order(
                {
                    "name": "Gaile Ng",
                    "address1": "幸神平1 C棟01室 BSWQ12AB",
                    "zip": "306-0608",
                    "countryCodeV2": "JP",
                },
                bill_cc="JP",
            )
        )
        self.assertTrue(ev["is_forwarder"])
        self.assertEqual(ev["service"], "Buyandship")

    def test_bs_prefix_without_known_hub(self):
        ev = evaluate_order(
            make_order(
                {
                    "name": "Taro BSABCDE Yamada",
                    "address1": "1-2-3 Sakura",
                    "zip": "100-0001",
                    "countryCodeV2": "JP",
                }
            )
        )
        self.assertTrue(ev["is_forwarder"])
        self.assertEqual(ev["service"], "Buyandship")

    def test_generic_code_in_both_fields(self):
        ev = evaluate_order(
            make_order(
                {
                    "name": "John ZX9KQ7 Doe",
                    "address1": "Warehouse ZX9KQ7 Bldg",
                    "zip": "543-0001",
                    "countryCodeV2": "JP",
                }
            )
        )
        self.assertTrue(ev["is_forwarder"])
        self.assertIsNone(ev["service"])  # generic forwarder, unknown service
        self.assertEqual(ev["confidence"], "medium")
        self.assertIn("repeated in name & address", " ".join(ev["reasons"]))

    def test_normal_residential_not_flagged(self):
        # romanized name has a 6-letter token (SUZUNE) but it is NOT repeated in the address.
        ev = evaluate_order(
            make_order(
                {
                    "name": "SUZUNE OMORI",
                    "address1": "６－１７－１２－１１０２",
                    "city": "台東区",
                    "zip": "110-0015",
                    "countryCodeV2": "JP",
                },
                bill_cc="JP",
            )
        )
        self.assertFalse(ev["is_forwarder"])

    def test_billing_mismatch_alone_not_flagged(self):
        ev = evaluate_order(
            make_order(
                {
                    "name": "Hanako Suzuki",
                    "address1": "2-2-2 Aoba",
                    "zip": "150-0001",
                    "countryCodeV2": "JP",
                },
                bill_cc="HK",
            )
        )
        self.assertFalse(ev["is_forwarder"])
        self.assertTrue(ev["signals"]["billing_mismatch"])  # recorded but not a trigger

    def test_fullwidth_zip_and_address_normalized(self):
        ev = evaluate_order(
            make_order(
                {
                    "name": "Test",
                    "address1": "幸神平１ Ｃ棟",
                    "zip": "３０６－０６０８",
                    "countryCodeV2": "JP",
                }
            )
        )
        self.assertTrue(ev["is_forwarder"])
        self.assertEqual(ev["service"], "Buyandship")

    def test_missing_shipping_address(self):
        ev = evaluate_order({"shippingAddress": None, "billingAddress": None})
        self.assertFalse(ev["is_forwarder"])


class TestForwarderGuardScan(unittest.TestCase):
    @patch.object(ShopifyGraphqlClient, "order_add_tags")
    @patch.object(ShopifyGraphqlClient, "run_query")
    def test_scan_applies_tags_to_matches_only(self, mock_run_query, mock_add_tags):
        mock_run_query.return_value = {
            "orders": {
                "pageInfo": {"hasNextPage": False, "endCursor": None},
                "nodes": [
                    make_order(
                        {
                            "name": "Mei Kwan BSZGRXHZ",
                            "address1": "幸神平1 C棟 BSZGRXHZ",
                            "zip": "306-0608",
                            "countryCodeV2": "JP",
                        },
                        name="#A",
                    ),
                    make_order(
                        {
                            "name": "Normal Person",
                            "address1": "1-1 Shibuya",
                            "zip": "150-0001",
                            "countryCodeV2": "JP",
                        },
                        name="#B",
                    ),
                ],
            }
        }
        client = ShopifyGraphqlClient(shop_name="dummy", access_token="dummy")
        guard = ForwarderGuard(client=client)
        matched = guard.scan(dry_run=False)

        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0][0]["name"], "#A")
        mock_add_tags.assert_called_once()
        _, called_tags = mock_add_tags.call_args[0]
        self.assertIn("forwarder-review", called_tags)
        self.assertIn("forwarder-buyandship", called_tags)

    @patch.object(ShopifyGraphqlClient, "order_add_tags")
    @patch.object(ShopifyGraphqlClient, "run_query")
    def test_dry_run_does_not_tag(self, mock_run_query, mock_add_tags):
        mock_run_query.return_value = {
            "orders": {
                "pageInfo": {"hasNextPage": False, "endCursor": None},
                "nodes": [
                    make_order(
                        {
                            "name": "x BSZGRXHZ",
                            "address1": "幸神平1 BSZGRXHZ",
                            "zip": "306-0608",
                            "countryCodeV2": "JP",
                        },
                        name="#A",
                    )
                ],
            }
        }
        client = ShopifyGraphqlClient(shop_name="dummy", access_token="dummy")
        ForwarderGuard(client=client).scan(dry_run=True)
        mock_add_tags.assert_not_called()


if __name__ == "__main__":
    unittest.main()
