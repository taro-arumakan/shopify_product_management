from google_api_interface.interface import GoogleApiInterface

def get(shop_name):
    from utils import credentials
    cred = credentials(shop_name)
    return GoogleApiInterface(cred.google_credential_path, sheet_id=cred.google_sheet_id)
