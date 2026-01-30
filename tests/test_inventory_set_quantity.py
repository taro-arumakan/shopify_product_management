import unittest
from unittest.mock import MagicMock, patch
from inventory_set_quantity import column_map, sku_quantity_map_from_sheet

class TestInventorySetQuantity(unittest.TestCase):
    def test_column_map(self):
        archive = column_map('archive-epke')
        self.assertEqual(archive['sku_index'], 4)
        
        kume = column_map('kumej')
        self.assertEqual(kume['sku_index'], 18)
        
        with self.assertRaises(ValueError):
            column_map('unknown_shop')

    @patch('inventory_set_quantity.utils.client')
    def test_sku_quantity_map_from_sheet(self, mock_client_factory):
        mock_client = MagicMock()
        mock_client_factory.return_value = mock_client
        mock_client.sheet_id = 'sheet_id'
        
        row_filler = [''] * 20
        
        row3 = row_filler.copy()
        row3[1] = '3/31 shipment'
        row3[18] = 'SKU1'
        row3[19] = '10'
        
        row4 = row_filler.copy()
        row4[1] = '4/1 shipment'
        row4[18] = 'SKU2'
        row4[19] = '5'

        mock_client.worksheet_rows.return_value = [
            [], [], [],
            row3,
            row4
        ]
        
        result = sku_quantity_map_from_sheet('kumej', 'title')
        
        self.assertIn('SKU1', result)
        self.assertEqual(result['SKU1'], 10)
        self.assertNotIn('SKU2', result)

if __name__ == '__main__':
    unittest.main()
