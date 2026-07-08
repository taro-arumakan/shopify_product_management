import unittest

from brands.rohseoul.adhoc.add_after_service_section import (
    has_balanced_tags,
    insert_after_service_section,
)
from brands.rohseoul.client import AFTER_SERVICE_HTML

CLEAN = (
    '<div id="cataldesignProduct">'
    "<h3>商品説明</h3><p>desc</p>"
    "<h3>手入れ方法</h3><p>care</p>"
    "<h3>サイズ・素材</h3><table></table>"
    "</div>"
)

# Some older products have no product-care section at all (e.g. non-leather items).
NO_CARE_SECTION = (
    '<div id="cataldesignProduct">'
    "<h3>商品説明</h3><p>desc</p>"
    "<h3>サイズ・素材</h3><table></table>"
    "</div>"
)

# Some older products render the care heading with a stray <br> before the
# closing tag (leftover from manual rich-text editing) and multiple <p> blocks.
STRAY_BR_IN_CARE_HEADING = (
    '<div id="cataldesignProduct">'
    "<h3>商品説明</h3><p>desc</p>"
    "<h3>手入れ方法<br>\n</h3><p>care line 1</p><p>care line 2</p>"
    "<h3>サイズ・素材</h3><table></table>"
    "</div>"
)

ALREADY_DONE = (
    '<div id="cataldesignProduct">'
    "<h3>商品説明</h3><p>desc</p>"
    "<h3>手入れ方法</h3><p>care</p>"
    f"{AFTER_SERVICE_HTML}"
    "<h3>サイズ・素材</h3><table></table>"
    "</div>"
)


class TestInsertAfterServiceSection(unittest.TestCase):
    def test_inserts_before_size_material_heading(self):
        result = insert_after_service_section(CLEAN)
        self.assertIn(AFTER_SERVICE_HTML, result)
        self.assertLess(result.index("手入れ方法"), result.index("アフターサービス"))
        self.assertLess(result.index("アフターサービス"), result.index("サイズ・素材"))
        self.assertTrue(has_balanced_tags(result))

    def test_balance_check_not_confused_by_thead(self):
        # <thead> contains "<th" as a prefix; a naive substring count of "<th"
        # over-counts opens relative to "</th>" closes. Real product size
        # tables all use <thead>, so this must not false-positive.
        html_with_thead = (
            '<div id="cataldesignProduct">'
            "<h3>商品説明</h3><p>desc</p>"
            "<h3>サイズ・素材</h3>"
            "<table><thead><tr><th>W</th><th>H</th></tr></thead>"
            "<tbody><tr><td>1</td><td>2</td></tr></tbody></table>"
            "</div>"
        )
        self.assertTrue(has_balanced_tags(html_with_thead))
        result = insert_after_service_section(html_with_thead)
        self.assertTrue(has_balanced_tags(result))

    def test_handles_product_with_no_care_section(self):
        result = insert_after_service_section(NO_CARE_SECTION)
        self.assertIn(AFTER_SERVICE_HTML, result)
        self.assertLess(result.index("商品説明"), result.index("アフターサービス"))
        self.assertLess(result.index("アフターサービス"), result.index("サイズ・素材"))

    def test_handles_stray_br_in_care_heading(self):
        result = insert_after_service_section(STRAY_BR_IN_CARE_HEADING)
        self.assertIn(AFTER_SERVICE_HTML, result)
        self.assertLess(result.index("care line 2"), result.index("アフターサービス"))
        self.assertLess(result.index("アフターサービス"), result.index("サイズ・素材"))

    def test_idempotent_when_already_present(self):
        result = insert_after_service_section(ALREADY_DONE)
        self.assertEqual(result, ALREADY_DONE)
        self.assertEqual(result.count("アフターサービス"), 1)

    def test_asserts_on_ambiguous_multiple_headings(self):
        broken = CLEAN.replace("</div>", "<h3>サイズ・素材</h3></div>")
        with self.assertRaises(AssertionError):
            insert_after_service_section(broken)


if __name__ == "__main__":
    unittest.main()
