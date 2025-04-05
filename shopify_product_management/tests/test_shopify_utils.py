import unittest
from unittest.mock import patch, MagicMock

class TestShopifyFunctions(unittest.TestCase):

    @patch('shopify_product_management.shopify_utils.run_query')
    def test_update_product_description(self, mock_run_query):
        mock_run_query.return_value = {
                'productSet': {
                    'product': {
                        'id': 'gid://shopify/Product/12345',
                        'descriptionHtml': '<p>New Description</p>'
                    },
                    'userErrors': []
                }
            }

        from shopify_product_management.shopify_utils import update_product_description
        result = update_product_description('shop_name', 'access_token', '12345', '<p>New Description</p>')

        self.assertEqual(result['productSet']['product']['descriptionHtml'], '<p>New Description</p>')
        mock_run_query.assert_called_once()

    def test_sanitize_image_name(self):
        from shopify_product_management.shopify_utils import sanitize_image_name
        result = sanitize_image_name('Dummy Product [Special Edition]_product_details_01.png')
        self.assertEqual(result, 'Dummy_Product_Special_Edition__product_details_01.png')

    def test_image_htmlfragment_in_description(self):
        from shopify_product_management.shopify_utils import image_htmlfragment_in_description
        result = image_htmlfragment_in_description('example_image.png', 2, 'https://cdn.shopify.com/s/files/1/0745/9435/3408')
        self.assertIn('<p class="reveal_tran_lr">', result)
        self.assertIn('<img src="https://cdn.shopify.com/s/files/1/0745/9435/3408/files/example_image.png"', result)

    @patch('shopify_product_management.shopify_utils.run_query')
    def test_product_id_by_title(self, mock_run_query):
        mock_run_query.return_value = {
            'products': {
                'nodes': [
                    {'id': 'gid://shopify/Product/12345', 'title': 'Test Product'}
                ]
            }
        }

        from shopify_product_management.shopify_utils import product_id_by_title
        product_id = product_id_by_title('shop_name', 'access_token', 'Test Product')

        self.assertEqual(product_id, 'gid://shopify/Product/12345')
        mock_run_query.assert_called_once()

    @patch('shopify_product_management.shopify_utils.run_query')
    def test_remove_product_media_by_product_id_no_media(self, mock_run_query):
        mock_run_query.return_value = {'product': {'media': {'nodes': []}}}

        from shopify_product_management.shopify_utils import remove_product_media_by_product_id
        result = remove_product_media_by_product_id('shop_name', 'access_token', '12345')

        self.assertTrue(result)
        mock_run_query.assert_called_once()

    @patch('shopify_product_management.shopify_utils.run_query')
    @patch('shopify_product_management.shopify_utils.medias_by_product_id')
    def test_assign_images_to_product(self, mock_medias_by_product_id, mock_run_query):
        mock_run_query.return_value = {
            'productCreateMedia': {
                'media': [{'alt': 'image1', 'status': 'READY'}],
                'userErrors': [],
                'product': {'id': 'gid://shopify/Product/12345', 'title': 'Test Product'}
            }
        }
        mock_medias_by_product_id.return_value = [
            {
                'alt': 'upload_20250218_KM-25SS-JP01-IV-S_00_2차_44.jpg',
                'id': 'gid://shopify/MediaImage/39672607768859',
                'image': {'url': 'https://cdn.shopify.com/s/files/1/0885/9435/0363/files/upload_20250218_KM-25SS-JP01-IV-S_00_2__44.jpg?v=1739867188'},
                'mediaContentType': 'IMAGE',
                'mediaErrors': [],
                'mediaWarnings': [],
                'status': 'READY'
            },
            {
                'alt': 'upload_20250218_KM-25SS-JP01-IV-S_03_20240508 KUME25SS250940 복사.jpg',
                'id': 'gid://shopify/MediaImage/39672607867163',
                'image': {'url': 'https://cdn.shopify.com/s/files/1/0885/9435/0363/files/upload_20250218_KM-25SS-JP01-IV-S_03_20240508_KUME25SS250940.jpg?v=1740622121'},
                'mediaContentType': 'IMAGE',
                'mediaErrors': [],
                'mediaWarnings': [],
                'status': 'READY'
            }]

        from shopify_product_management.shopify_utils import assign_images_to_product
        resource_urls = ['https://example.com/image1.png']
        alts = ['image1']
        result = assign_images_to_product('shop_name', 'access_token', resource_urls, alts, 'gid://shopify/Product/12345')

        self.assertIsNone(result)  # No exception raised means success
        mock_run_query.assert_called_once()

    @patch('shopify_product_management.shopify_utils.run_query')
    def test_update_product_description_metafield(self, mock_run_query):
        mock_run_query.return_value = {
            'productUpdate': {
                'product': {'metafields': [{'key': 'product_description',
                                            'namespace': 'custom',
                                            'value': 'Updated'}]},
                'userErrors': []
            }
        }
        from shopify_product_management.shopify_utils import update_product_description_metafield
        result = update_product_description_metafield('shop_name', 'access_token', '12345', {'rich_text': 'Updated'})

        self.assertIsNotNone(result)
        mock_run_query.assert_called_once()


if __name__ == '__main__':
    unittest.main()
