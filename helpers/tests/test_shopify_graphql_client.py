import os
print(os.getcwd())

import unittest
from unittest.mock import patch
from helpers.shopify_graphql_client.client import ShopifyGraphqlClient
class TestShopifyFunctions(unittest.TestCase):

    @patch.object(ShopifyGraphqlClient, 'run_query')
    def test_update_product_description(self, mock_run_query):
        mock_run_query.return_value = {
                'productUpdate': {
                    'product': {
                        'id': 'gid://shopify/Product/12345',
                        'descriptionHtml': '<p>New Description</p>'
                    },
                    'userErrors': []
                }
            }

        client = ShopifyGraphqlClient(shop_name='dummy', access_token='dummy')
        result = client.update_product_description('12345', '<p>New Description</p>')

        self.assertEqual(result['productUpdate']['product']['descriptionHtml'], '<p>New Description</p>')
        mock_run_query.assert_called_once()

    def test_sanitize_image_name(self):
        from helpers.shopify_graphql_client import ShopifyGraphqlClient
        sgc = ShopifyGraphqlClient('dummy_shop_name', 'dummy_access_token')
        result = sgc.sanitize_image_name('Dummy Product [Special Edition]_product_details_01.png')
        self.assertEqual(result, 'Dummy_Product_Special_Edition__product_details_01.png')

    def test_image_htmlfragment_in_description(self):
        from helpers.shopify_graphql_client import ShopifyGraphqlClient
        sgc = ShopifyGraphqlClient('dummy_shop_name', 'dummy_access_token')
        result = sgc.image_htmlfragment_in_description('example_image.png', 2, 'https://cdn.shopify.com/s/files/1/0745/9435/3408')
        self.assertIn('<p class="reveal_tran_lr">', result)
        self.assertIn('<img src="https://cdn.shopify.com/s/files/1/0745/9435/3408/files/example_image.png"', result)

    @patch.object(ShopifyGraphqlClient, 'run_query')
    def test_product_id_by_title(self, mock_run_query):
        mock_run_query.return_value = {
            'products': {
                'nodes': [
                    {'id': 'gid://shopify/Product/12345', 'title': 'Test Product'}
                ]
            }
        }

        client = ShopifyGraphqlClient(shop_name='dummy', access_token='dummy')
        product_id = client.product_id_by_title('Test Product')

        self.assertEqual(product_id, 'gid://shopify/Product/12345')
        mock_run_query.assert_called_once()

    @patch.object(ShopifyGraphqlClient, 'run_query')
    def test_remove_product_media_by_product_id_no_media(self, mock_run_query):
        mock_run_query.return_value = {'product': {'media': {'nodes': []}}}

        client = ShopifyGraphqlClient(shop_name='dummy', access_token='dummy')
        result = client.remove_product_media_by_product_id('12345')

        self.assertTrue(result)
        mock_run_query.assert_called_once()

    @patch.object(ShopifyGraphqlClient, 'run_query')
    @patch.object(ShopifyGraphqlClient, 'medias_by_product_id')
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

        client = ShopifyGraphqlClient(shop_name='dummy', access_token='dummy')
        resource_urls = ['https://example.com/image1.png']
        alts = ['image1']
        result = client.assign_images_to_product(resource_urls, alts, 'gid://shopify/Product/12345')

        self.assertDictEqual(result, {'productCreateMedia':
                                        {'media': [{'alt': 'image1', 'status': 'READY'}],
                                         'userErrors': [],
                                         'product': {'id': 'gid://shopify/Product/12345', 'title': 'Test Product'}}})
        mock_run_query.assert_called_once()

    @patch.object(ShopifyGraphqlClient, 'run_query')
    def test_update_product_description_metafield(self, mock_run_query):
        mock_run_query.return_value = {
            'productUpdate': {
                'product': {'metafields': [{'key': 'product_description',
                                            'namespace': 'custom',
                                            'value': 'Updated'}]},
                'userErrors': []
            }
        }
        client = ShopifyGraphqlClient(shop_name='dummy', access_token='dummy')
        result = client.update_product_description_metafield('12345', {'rich_text': 'Updated'})

        self.assertIsNotNone(result)
        mock_run_query.assert_called_once()


if __name__ == '__main__':
    unittest.main()
