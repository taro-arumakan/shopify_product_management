import unittest
from unittest.mock import patch, MagicMock
import utils
from brands.kume.client import KumeClient
from brands.archivepke.client import ArchivepkeClient

class TestUtils(unittest.TestCase):
    
    @patch.dict('os.environ', {
        'kumej-ACCESS_TOKEN': 'dummy_token',
        'GOOGLE_CREDENTIAL_PATH': '/dummy/path',
        'kumej-GSPREAD_ID': 'dummy_sheet_id'
    })
    @patch('helpers.client.Client.__init__', return_value=None)
    def test_client_kume(self, mock_client_init):
        # Using os.environ instead of mocking credentials/init directly
        client = utils.client("kume")
        self.assertIsInstance(client, KumeClient)
        
    @patch.dict('os.environ', {
        'archive-epke-ACCESS_TOKEN': 'dummy_token',
        'GOOGLE_CREDENTIAL_PATH': '/dummy/path',
        'archive-epke-GSPREAD_ID': 'dummy_sheet_id'
    })
    @patch('helpers.client.Client.__init__', return_value=None)
    def test_client_archivepke_aliases(self, mock_client_init):
        aliases = ["archive-epke", "archivepke", "archivépke", "archive"]
        for alias in aliases:
            client = utils.client(alias)
            self.assertIsInstance(client, ArchivepkeClient)

    @patch('dotenv.load_dotenv', return_value=True)
    @patch('os.environ', {
        'shop1-ACCESS_TOKEN': 'secret_token',
        'GOOGLE_CREDENTIAL_PATH': '/path/to/json',
        'shop1-GSPREAD_ID': 'sheet_id'
    })
    def test_credentials_loading(self, mock_dotenv):
        cred = utils.credentials("shop1")
        self.assertEqual(cred.access_token, "secret_token")
        self.assertEqual(cred.shop_name, "shop1")
        self.assertEqual(cred.google_credential_path, "/path/to/json")
        self.assertEqual(cred.google_sheet_id, "sheet_id")

if __name__ == "__main__":
    unittest.main()
