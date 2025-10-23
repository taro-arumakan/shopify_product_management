from helpers.client import Client
from helpers.exceptions import (
    MultipleProductsFoundException,
    NoProductsFoundException,
    MultipleVariantsFoundException,
    NoVariantsFoundException,
)


def credentials(shop_name):
    import os
    from dotenv import load_dotenv
    from dataclasses import dataclass

    @dataclass
    class Credentials:
        shop_name: str
        access_token: str
        google_credential_path: str
        google_sheet_id: str

    assert load_dotenv(override=True)
    access_token = os.environ[f"{shop_name}-ACCESS_TOKEN"]
    google_credential_path = os.environ["GOOGLE_CREDENTIAL_PATH"]
    google_sheet_id = os.environ.get(f"{shop_name}-GSPREAD_ID")
    res = {
        "shop_name": shop_name,
        "access_token": access_token,
        "google_credential_path": google_credential_path,
        "google_sheet_id": google_sheet_id,
    }
    return Credentials(**res)


def client(shop_name: str) -> Client:
    if shop_name.lower() in ["alvanas", "alvana"]:
        from brands.alvana.client import AlvanaClient

        res = AlvanaClient()
    elif shop_name.lower() in ["ssilkr", "ssil"]:
        from brands.ssil.client import SsilClient

        res = SsilClient()
    elif shop_name.lower() == "rohseoul":
        from brands.rohseoul.client import RohseoulClient

        res = RohseoulClient()
    else:
        cred = credentials(shop_name)
        res = Client(
            shop_name=cred.shop_name,
            access_token=cred.access_token,
            google_credential_path=cred.google_credential_path,
            sheet_id=cred.google_sheet_id,
        )
    return res
