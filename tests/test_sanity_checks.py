import unittest

from brands.alvana.client import AlvanaClient
from brands.asheis.client import AsheisClient
from brands.gbh.client import GbhClient, GbhClientNoOptions
from brands.kume.client import KumeClient
from brands.client.sanity_checks import SanityChecks


class TestCheckRequiredFields(unittest.TestCase):
    def setUp(self):
        class Checks(SanityChecks):
            REQUIRED_PRODUCT_INPUT_FIELDS = ("product_care",)

        self.checks = Checks()

    def test_flags_absent_none_empty_and_whitespace(self):
        # A blank sheet cell drops the key entirely; the others guard against a
        # value that survives parsing but is still empty.
        product_inputs = [
            {"title": "ABSENT"},
            {"title": "NONE", "product_care": None},
            {"title": "EMPTY", "product_care": ""},
            {"title": "SPACES", "product_care": "  \n"},
        ]
        self.assertEqual(
            self.checks.check_required_fields(product_inputs),
            [
                "Blank product_care for ABSENT",
                "Blank product_care for NONE",
                "Blank product_care for EMPTY",
                "Blank product_care for SPACES",
            ],
        )

    def test_passes_a_filled_field(self):
        self.assertEqual(
            self.checks.check_required_fields(
                [{"title": "T", "product_care": "手洗い"}]
            ),
            [],
        )

    def test_nothing_required_by_default(self):
        self.assertEqual(SanityChecks().check_required_fields([{"title": "T"}]), [])


class TestCheckExpectedFields(unittest.TestCase):
    def setUp(self):
        class Checks(SanityChecks):
            EXPECTED_PRODUCT_INPUT_FIELDS = ("product_care",)

        self.checks = Checks()

    def test_blank_only_warns(self):
        with self.assertLogs("brands.client.sanity_checks", "WARNING") as logs:
            res = self.checks.check_expected_fields([{"title": "ABSENT"}])
        self.assertEqual(res, ["Blank product_care for ABSENT"])
        self.assertEqual([r.levelname for r in logs.records], ["WARNING"])

    def test_no_warning_for_a_filled_field(self):
        self.assertEqual(
            self.checks.check_expected_fields(
                [{"title": "T", "product_care": "手洗い"}]
            ),
            [],
        )

    def test_nothing_expected_by_default(self):
        self.assertEqual(SanityChecks().check_expected_fields([{"title": "T"}]), [])


class TestFieldDeclarations(unittest.TestCase):
    """Clients whose creation path reads product_care unconditionally."""

    def test_clients_that_read_product_care_require_it(self):
        for client_class in (AlvanaClient, KumeClient, GbhClient):
            with self.subTest(client_class.__name__):
                self.assertIn(
                    "product_care", client_class.REQUIRED_PRODUCT_INPUT_FIELDS
                )

    def test_gbh_no_options_opts_back_out(self):
        # Maps product_care but its description template never reads it, so the
        # requirement inherited from GbhClient must not apply.
        self.assertEqual(GbhClientNoOptions.REQUIRED_PRODUCT_INPUT_FIELDS, ())

    def test_asheis_expects_product_care_without_requiring_it(self):
        # Some ASHEIS products have no care text; update_metafields skips the
        # metafield, so a blank warns rather than failing the sanity check.
        self.assertEqual(AsheisClient.REQUIRED_PRODUCT_INPUT_FIELDS, ())
        self.assertEqual(AsheisClient.EXPECTED_PRODUCT_INPUT_FIELDS, ("product_care",))


if __name__ == "__main__":
    unittest.main()
