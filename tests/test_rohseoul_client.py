import unittest

from brands.rohseoul.client import RohseoulClient


class TestRohseoulDescription(unittest.TestCase):
    def setUp(self):
        self.client = RohseoulClient.__new__(RohseoulClient)

    def test_get_description_html_includes_after_service_section(self):
        product_input = {
            "title": "TEST BAG",
            "description": "テスト用の商品説明です。",
            "material": "Cowhide leather",
            "made_in": "韓国",
            "size_text": "W 30\nH 20\nD 10",
        }
        html = self.client.get_description_html(product_input)

        self.assertIn("<h3>アフターサービス</h3>", html)
        self.assertIn(
            '<a href="https://rohseoul.jp/pages/warranty-certificate-and-after-service">こちら</a>',
            html,
        )
        care_idx = html.index("<h3>手入れ方法</h3>")
        after_service_idx = html.index("<h3>アフターサービス</h3>")
        size_idx = html.index("<h3>サイズ・素材</h3>")
        self.assertTrue(care_idx < after_service_idx < size_idx)


if __name__ == "__main__":
    unittest.main()
