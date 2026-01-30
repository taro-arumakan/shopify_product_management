import unittest
from helpers.client import Client
from unittest.mock import MagicMock
import pathlib
import datetime

class TestClientHelpers(unittest.TestCase):
    def setUp(self):
        self.client = Client.__new__(Client)
        self.client.shop_name = 'test_shop'
        
    def test_segment_options_list_by_key_option(self):
        option_dicts = [
            {'option_values': {'Color': 'Red', 'Size': 'S'}, 'sku': 'SKU1'},
            {'option_values': {'Color': 'Red', 'Size': 'M'}, 'sku': 'SKU2'},
            {'option_values': {'Color': 'Blue', 'Size': 'S'}, 'sku': 'SKU3'},
            {'option_values': {'Color': 'Blue', 'Size': 'M'}, 'sku': 'SKU4'},
        ]
        
        result = self.client.segment_options_list_by_key_option(option_dicts)
        
        self.assertEqual(len(result), 2)
        
        self.assertEqual(len(result[0]), 2)
        self.assertEqual(result[0][0]['option_values']['Color'], 'Red')
        self.assertEqual(result[0][1]['option_values']['Color'], 'Red')
        
        self.assertEqual(len(result[1]), 2)
        self.assertEqual(result[1][0]['option_values']['Color'], 'Blue')
        self.assertEqual(result[1][1]['option_values']['Color'], 'Blue')

    def test_segment_options_single_group(self):
        option_dicts = [
            {'option_values': {'Size': 'S'}, 'sku': 'SKU1'},
            {'option_values': {'Size': 'M'}, 'sku': 'SKU2'},
        ]
        
        result = self.client.segment_options_list_by_key_option(option_dicts)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0]['sku'], 'SKU1')
        self.assertEqual(result[1][0]['sku'], 'SKU2')

    def test_product_input_to_skus(self):
        self.client.populate_option_dicts = MagicMock(return_value=[
            {'sku': 'SKU1'},
            {'sku': 'SKU2'},
            {'sku': 'SKU3'}
        ])
        
        product_input = {'some': 'data'}
        result = self.client.product_input_to_skus(product_input)
        
        self.assertEqual(result, ['SKU1', 'SKU2', 'SKU3'])
        self.client.populate_option_dicts.assert_called_once_with(product_input)

    def test_get_sku_stocks_map(self):
        self.client.get_variants_level_info = MagicMock(return_value=[
            {'sku': 'SKU1', 'stock': 10},
            {'sku': 'SKU2', 'stock': 5},
            {'sku': 'SKU3'}
        ])
        
        product_input = {'some': 'data'}
        result = self.client.get_sku_stocks_map(product_input)
        
        expected = {
            'SKU1': 10,
            'SKU2': 5,
            'SKU3': 0
        }
        self.assertEqual(result, expected)
        self.client.get_variants_level_info.assert_called_once_with(product_input)

    def test_product_id_by_product_input_with_handle(self):
        self.client.product_id_by_handle = MagicMock(return_value='gid://shopify/Product/123')
        self.client.product_id_by_title = MagicMock()
        
        product_input = {'title': 'My Product', 'handle': 'my-product'}
        result = self.client.product_id_by_product_input(product_input)
        
        self.assertEqual(result, 'gid://shopify/Product/123')
        self.client.product_id_by_handle.assert_called_once_with('my-product')
        self.client.product_id_by_title.assert_not_called()

    def test_create_product_and_activate_inventory_with_options(self):
        self.client.populate_option_dicts = MagicMock(return_value=[
            {'option_values': {'Size': 'S'}},
            {'option_values': {'Size': 'M'}}
        ])
        self.client.product_create = MagicMock(return_value={'id': 'prod1'})
        self.client.enable_and_activate_inventory_by_product_input = MagicMock(return_value=['inv1'])
        
        product_input = {'title': 'Test Prod', 'price': 100, 'sku': 'SKU1'}
        result = self.client.create_product_and_activate_inventory(
            product_input, 'Vendor', '<div>Desc</div>', ['tag1'], ['Loc1']
        )
        
        self.client.product_create.assert_called_once()
        self.client.enable_and_activate_inventory_by_product_input.assert_called_once()
        self.assertEqual(result, ({'id': 'prod1'}, ['inv1']))

    def test_create_product_and_activate_inventory_no_options(self):
        self.client.populate_option_dicts = MagicMock(return_value=[
            {'option_values': {}},
        ])
        self.client.product_create_default_variant = MagicMock(return_value={'id': 'prod1'})
        self.client.enable_and_activate_inventory_by_product_input = MagicMock(return_value=['inv1'])
        
        product_input = {'title': 'Test Prod', 'price': 100, 'sku': 'SKU1'}
        result = self.client.create_product_and_activate_inventory(
            product_input, 'Vendor', '<div>Desc</div>', ['tag1'], ['Loc1']
        )
        
        self.client.product_create_default_variant.assert_called_once()
        self.client.enable_and_activate_inventory_by_product_input.assert_called_once()
        self.assertEqual(result, ({'id': 'prod1'}, ['inv1']))

    def test_add_product_images(self):
        self.client.drive_images_to_local = MagicMock(return_value=['path/to/img1.jpg'])
        self.client.upload_and_assign_images_to_product = MagicMock(return_value={'media': []})
        
        result = self.client.add_product_images(
            'prod1', 'drive1', '/tmp', 'prefix', True
        )
        
        self.client.drive_images_to_local.assert_called_once_with('drive1', '/tmp', filename_prefix='prefix')
        self.client.upload_and_assign_images_to_product.assert_called_once_with('prod1', ['path/to/img1.jpg'], True)

    def test_process_product_images(self):
        self.client.product_id_by_title = MagicMock(return_value='prod1')
        self.client.populate_drive_ids_and_skuss = MagicMock(return_value=(
            ['drive1', 'drive2'],
            [['SKU1'], ['SKU2']]
        ))
        self.client.add_product_images = MagicMock(side_effect=[
            [{'productCreateMedia': {'media': [{'id': 'media1'}]}}],
            [{'productCreateMedia': {'media': [{'id': 'media2'}]}}]
        ])
        self.client.assign_image_to_skus = MagicMock(return_value='assigned')
        
        with unittest.mock.patch('pathlib.Path.home', return_value=pathlib.Path('/tmp')):
            with unittest.mock.patch('helpers.client.datetime') as mock_datetime:
                mock_datetime.date.today.return_value = datetime.date(2023, 1, 1)
                
                result = self.client.process_product_images({'title': 'Test'})
        
        self.assertEqual(len(result), 4)
        self.client.product_id_by_title.assert_called_once()
        self.assertEqual(self.client.add_product_images.call_count, 2)
        self.assertTrue(self.client.add_product_images.call_args_list[0][1]['remove_existings'])
        self.assertFalse(self.client.add_product_images.call_args_list[1][1]['remove_existings'])

    def test_enable_and_activate_inventory_by_product_input(self):
        self.client.product_input_to_skus = MagicMock(return_value=['SKU1', 'SKU2'])
        self.client.enable_and_activate_inventory_by_sku = MagicMock(side_effect=['res1', 'res2'])
        
        result = self.client.enable_and_activate_inventory_by_product_input({'data': 'test'}, ['Loc1'])
        
        self.assertEqual(result, ['res1', 'res2'])
        self.client.product_input_to_skus.assert_called_once()
        self.assertEqual(self.client.enable_and_activate_inventory_by_sku.call_count, 2)

    def test_update_stocks(self):
        self.client.location_id_by_name = MagicMock(return_value='loc_id_1')
        self.client.get_sku_stocks_map = MagicMock(return_value={'SKU1': 10, 'SKU2': 5})
        self.client.set_inventory_quantity_by_sku_and_location_id = MagicMock(return_value='success')
        
        product_inputs = [{'data': '1'}]
        result = self.client.update_stocks(product_inputs, 'Loc1')
        
        self.client.location_id_by_name.assert_called_once_with('Loc1')
        self.assertEqual(self.client.set_inventory_quantity_by_sku_and_location_id.call_count, 2)
        calls = self.client.set_inventory_quantity_by_sku_and_location_id.call_args_list
        self.assertTrue(any(c[0] == ('SKU1', 'loc_id_1', 10) for c in calls))
        self.assertTrue(any(c[0] == ('SKU2', 'loc_id_1', 5) for c in calls))

    def test_publish_products(self):
        self.client.product_id_by_product_input = MagicMock(side_effect=['id1', 'id2'])
        self.client.activate_and_publish_by_product_id = MagicMock()
        
        product_inputs = [{'p': 1}, {'p': 2}]
        self.client.publish_products(product_inputs, scheduled_time='time')
        
        self.assertEqual(self.client.product_id_by_product_input.call_count, 2)
        self.client.activate_and_publish_by_product_id.assert_called_with('id2', scheduled_time='time')

    def test_send_email(self):
        with unittest.mock.patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            with unittest.mock.patch('os.getenv') as mock_getenv:
                mock_getenv.side_effect = lambda k, d=None: {
                    'SMTP_HOST': 'smtp.test.com',
                    'SMTP_PORT': '587',
                    'SMTP_USER': 'user',
                    'SMTP_PASS': 'pass',
                    'SMTP_FROM_ADDR': 'from@test.com'
                }.get(k, d)
                
                self.client.send_email('Subject', 'Body', ['to@test.com'])
                
                mock_smtp.assert_called_with('smtp.test.com', 587)
                mock_server.starttls.assert_called_once()
                mock_server.login.assert_called_with('user', 'pass')
                mock_server.send_message.assert_called_once()
                msg = mock_server.send_message.call_args[0][0]
                self.assertEqual(msg['Subject'], 'Subject')
                self.assertEqual(msg['From'], 'from@test.com')
                self.assertEqual(msg['To'], 'to@test.com')

    def test_replace_images_by_skus(self):
        self.client.medias_by_sku = MagicMock(return_value=[{'id': 'old_media_1'}])
        self.client.drive_images_to_local = MagicMock(return_value=['/tmp/image1.jpg'])
        self.client.generate_staged_upload_targets = MagicMock(return_value=[{'resourceUrl': 'url1'}])
        self.client.upload_images_to_shopify_parallel = MagicMock()
        self.client.product_id_by_sku = MagicMock(return_value='prod_id')
        self.client.remove_product_media_by_product_id = MagicMock()
        self.client.assign_images_to_product = MagicMock()
        self.client.media_by_product_id_by_file_name = MagicMock(return_value={'id': 'new_media_id'})
        self.client.assign_image_to_skus = MagicMock()
        
        with unittest.mock.patch('pathlib.Path.home', return_value=pathlib.Path('/tmp')):
            with unittest.mock.patch('helpers.client.datetime') as mock_datetime:
                mock_datetime.date.today.return_value = datetime.date(2023, 1, 1)
                self.client.replace_images_by_skus(['SKU1'], 'folder_id', '/tmp', 'prefix')
        
        self.client.medias_by_sku.assert_called_with('SKU1')
        self.client.drive_images_to_local.assert_called_once()
        self.client.generate_staged_upload_targets.assert_called_once()
        self.client.upload_images_to_shopify_parallel.assert_called_once()
        self.client.remove_product_media_by_product_id.assert_called_with('prod_id', ['old_media_1'])
        self.client.assign_images_to_product.assert_called_with(['url1'], alts=['image1.jpg'], product_id='prod_id')
        self.client.assign_image_to_skus.assert_called_with('prod_id', 'new_media_id', ['SKU1'])

    def test_add_variants_from_product_input(self):
        self.client.populate_option_dicts = MagicMock(return_value=[{'option_values': {'Size': 'S'}}])
        self.client.segment_options_list_by_key_option = MagicMock(return_value=[
            [{'option_values': {'Size': 'S'}, 'price': 100, 'stock': 10}]
        ])
        self.client.populate_drive_ids_and_skuss = MagicMock(return_value=(['drive1'], [['SKU1']]))
        self.client.product_id_by_title = MagicMock(return_value='prod_id')
        self.client.location_id_by_name = MagicMock(return_value='loc_id')
        
        self.client.add_product_images = MagicMock(return_value=[
            {'productCreateMedia': {'media': [{'id': 'media_id'}]}}
        ])
        self.client.variants_add = MagicMock()
        self.client.enable_and_activate_inventory_by_product_id = MagicMock()
        
        product_input = {'title': 'Test Product'}
        location_names = ['Loc1']
        
        with unittest.mock.patch('pathlib.Path.home', return_value=pathlib.Path('/tmp')):
            with unittest.mock.patch('helpers.client.datetime') as mock_datetime:
                mock_datetime.date.today.return_value = datetime.date(2023, 1, 1)
                self.client.add_variants_from_product_input(product_input, location_names)
        
        self.client.add_product_images.assert_called_once()
        self.client.variants_add.assert_called_once()
        
        call_kwargs = self.client.variants_add.call_args[1]
        self.assertEqual(call_kwargs['product_id'], 'prod_id')
        self.assertEqual(call_kwargs['skus'], ['SKU1'])
        self.assertEqual(call_kwargs['variant_media_ids'], ['media_id'])
        self.assertEqual(call_kwargs['prices'], [100])

        self.client.enable_and_activate_inventory_by_product_id.assert_called_with('prod_id', location_names=location_names)

if __name__ == "__main__":
    unittest.main()
