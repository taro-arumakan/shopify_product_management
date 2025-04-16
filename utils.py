import os
from dotenv import load_dotenv
from collections import namedtuple

def credentials(shop_name):
    assert(load_dotenv(override=True))
    access_token = os.environ[f'{shop_name}-ACCESS_TOKEN']
    google_credential_path = os.environ['GOOGLE_CREDENTIAL_PATH']
    google_sheet_id = os.environ.get(f'{shop_name}-GSPREAD_ID')
    res = {
            'shop_name': shop_name,
            'access_token': access_token,
            'google_credential_path': google_credential_path,
            'google_sheet_id': google_sheet_id
        }
    cred = namedtuple('Credentials', res.keys())
    return cred(*res.values())
