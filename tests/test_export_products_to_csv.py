import unittest
from export_products_to_csv import get_product_rows, SHOPIFY_COLS

class TestExportProductsToCsv(unittest.TestCase):
    def test_get_product_rows_simple_product(self):
        brand_name = "test_brand"
        product = {
            "id": "gid://shopify/Product/1",
            "title": "Test Product",
            "handle": "test-product",
            "descriptionHtml": "<p>Description</p>",
            "vendor": "Test Vendor",
            "tags": ["tag1", "tag2"],
            "status": "ACTIVE",
            "media": {
                "nodes": [
                    {"image": {"url": "http://example.com/image.jpg"}}
                ]
            },
            "variants": {
                "nodes": [
                    {
                        "sku": "SKU1",
                        "price": "100.00",
                        "selectedOptions": [
                            {"name": "Size", "value": "S"}
                        ],
                        "image": {"url": "http://example.com/variant_image.jpg"}
                    }
                ]
            }
        }

        rows = get_product_rows(product, brand_name)

        self.assertEqual(len(rows), 1)
        row = rows[0]

        self.assertEqual(row["Handle"], "test-product")
        self.assertEqual(row["Title"], "Test Product")
        self.assertEqual(row["Body (HTML)"], "<p>Description</p>")
        self.assertEqual(row["Vendor"], "TEST_BRAND")
        self.assertEqual(row["Tags"], "tag1,tag2")
        self.assertEqual(row["Published"], "TRUE")

        self.assertEqual(row["Variant SKU"], "SKU1")
        self.assertEqual(row["Variant Price"], "100.00")
        self.assertEqual(row["Option1 Name"], "Size")
        self.assertEqual(row["Option1 Value"], "S")

        self.assertEqual(row["Image Src"], "http://example.com/image.jpg")
        self.assertEqual(row["Variant Image"], "http://example.com/variant_image.jpg")
    
    def test_get_product_rows_multiple_variants(self):
        brand_name = "test_brand"
        product = {
            "id": "gid://shopify/Product/1",
            "title": "Test Product",
            "handle": "test-product",
            "tags": [],
            "status": "DRAFT",
            "variants": {
                "nodes": [
                    {
                        "sku": "SKU1",
                        "price": "100",
                        "selectedOptions": [{"name": "Size", "value": "S"}]
                    },
                    {
                        "sku": "SKU2",
                        "price": "100",
                        "selectedOptions": [{"name": "Size", "value": "M"}]
                    }
                ]
            }
        }

        rows = get_product_rows(product, brand_name)

        self.assertEqual(len(rows), 2)
        
        self.assertEqual(rows[0]["Variant SKU"], "SKU1")
        self.assertEqual(rows[0]["Title"], "Test Product")
        self.assertEqual(rows[0]["Published"], "FALSE")
        self.assertEqual(rows[0]["Status"], "draft")

        self.assertEqual(rows[1]["Variant SKU"], "SKU2")
        self.assertEqual(rows[1]["Title"], "Test Product") 
        self.assertEqual(rows[1]["Image Src"], "")

    def test_shopify_cols_presence(self):
        brand_name = "test"
        product = {"variants": {"nodes": [{}]}}
        rows = get_product_rows(product, brand_name)
        
        for col in SHOPIFY_COLS:
            self.assertIn(col, rows[0])

if __name__ == '__main__':
    unittest.main()
