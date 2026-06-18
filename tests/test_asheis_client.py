import re
import unittest
from brands.asheis.client import AsheisClient


def table_to_rows(html):
    """Parse a generated size table back into [headers, *data_rows] of cell lists."""
    return [
        re.findall(r"<t[hd]>(.*?)</t[hd]>", tr, re.S)
        for tr in re.findall(r"<tr>(.*?)</tr>", html, re.S)
    ]


class TestAsheisSizeField(unittest.TestCase):
    def setUp(self):
        self.client = AsheisClient.__new__(AsheisClient)

    def size_field(self, size_text, sizes=("F",)):
        product_input = {
            "title": "T",
            "size_text": size_text,
            "options": [{"カラー": "BLACK", "options": [{"サイズ": s} for s in sizes]}],
        }
        return table_to_rows(self.client.get_size_field(product_input))

    def test_multi_size_with_lining_line(self):
        size_text = (
            "[0] 着丈116 / 身幅73 / 袖幅(二の腕)45.5\n"
            "裏地：背裏\n"
            "[1] 着丈122 / 身幅73 / 袖幅(二の腕)45.5\n"
            "裏地：背裏"
        )
        rows = self.size_field(size_text, sizes=["0(90)", "1(91)"])
        self.assertEqual(rows[0], ["Size", "着丈", "身幅", "袖幅(二の腕)", "裏地"])
        self.assertEqual(rows[1], ["0", "116", "73", "45.5", "背裏"])
        self.assertEqual(rows[2], ["1", "122", "73", "45.5", "背裏"])

    def test_single_size_without_bracket_infers_size(self):
        # no [F] prefix; sole variant size F(00) -> "F"
        rows = self.size_field("着丈65 / 身幅55\n裏地：総裏", sizes=["F(00)"])
        self.assertEqual(rows[0], ["Size", "着丈", "身幅", "裏地"])
        self.assertEqual(rows[1], ["F", "65", "55", "総裏"])

    def test_value_annotations_preserved(self):
        rows = self.size_field("[F] ヒップ104.5(ﾀｯｸなし) / もも周り86(裏地寸)")
        self.assertEqual(rows[1], ["F", "104.5(ﾀｯｸなし)", "86(裏地寸)"])

    def test_placeholder_value_becomes_empty(self):
        rows = self.size_field(
            "[1] 着丈68 / 身幅◯◯\n[2] 着丈70 / 身幅◯◯", sizes=["1", "2"]
        )
        self.assertEqual(rows[0], ["Size", "着丈", "身幅"])
        self.assertEqual(rows[1], ["1", "68", ""])
        self.assertEqual(rows[2], ["2", "70", ""])

    def test_label_only_value_empty(self):
        rows = self.size_field("[1] ウエスト(ｺﾞﾑ上がり) / ヒップ97", sizes=["1"])
        self.assertEqual(rows[0], ["Size", "ウエスト(ｺﾞﾑ上がり)", "ヒップ"])
        self.assertEqual(rows[1], ["1", "", "97"])

    def test_range_value_preserved(self):
        rows = self.size_field("[F] 長さ100 / ウエスト72.5〜82.5")
        self.assertEqual(rows[1], ["F", "100", "72.5〜82.5"])

    def test_section_grouped_split_on_space(self):
        rows = self.size_field("[F] (ボレロ)着丈32 / ゆき80 (インナー)着丈57 / 身幅32")
        self.assertEqual(
            rows[0], ["Size", "(ボレロ)着丈", "ゆき", "(インナー)着丈", "身幅"]
        )
        self.assertEqual(rows[1], ["F", "32", "80", "57", "32"])

    def test_no_size_text_returns_empty(self):
        self.assertEqual(self.client.get_size_field({"title": "T"}), "")
        self.assertEqual(
            self.client.get_size_field({"title": "T", "size_text": ""}), ""
        )

    def test_sole_size_blank_when_ambiguous(self):
        product_input = {
            "title": "T",
            "options": [
                {
                    "カラー": "BLACK",
                    "options": [{"サイズ": "1(91)"}, {"サイズ": "2(92)"}],
                }
            ],
        }
        self.assertEqual(self.client.sole_size(product_input), "")


class TestAsheisDescription(unittest.TestCase):
    def setUp(self):
        self.client = AsheisClient.__new__(AsheisClient)

    def test_get_description_html(self):
        product_input = {
            "title": "OVERSIZED NYLON COAT",
            "description": '"軽さがありながらも\nハリ感のあるコート。"',
            "material": "表地　ナイロン55％\n裏地　ポリエステル100％",
            "made_in": "日本",
        }
        html = self.client.get_description_html(product_input)
        self.assertIn('<div id="asheisProduct">', html)
        self.assertIn("<p>軽さがありながらも<br>ハリ感のあるコート。</p>", html)
        self.assertIn("<td>表地　ナイロン55％<br>裏地　ポリエステル100％</td>", html)
        self.assertIn("<td>日本</td>", html)
        self.assertNotIn("品番", html)


if __name__ == "__main__":
    unittest.main()
