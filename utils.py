from helpers.client import Client
from brands.brandclientbase import BrandClientBase
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


def client(shop_name: str) -> BrandClientBase:
    if shop_name.lower() in ["archive-epke", "archivepke"]:
        from brands.archivepke.client import ArchivepkeClient

        res = ArchivepkeClient()

    elif shop_name.lower() in ["alvanas", "alvana"]:
        from brands.alvana.client import AlvanaClient

        res = AlvanaClient()

    elif shop_name.lower() in ["apricot-studios", "apricot", "apricotstudios"]:
        from brands.apricotstudios.client import ApricotStudiosClient

        res = ApricotStudiosClient(None, None)

    elif shop_name.lower() in ["blossom", "blossomhcompany"]:
        from brands.blossom.client import BlossomClient

        res = BlossomClient()

    elif shop_name.lower() in ["gbhjapan", "gbh"]:
        from brands.gbh.client import GbhClient

        res = GbhClient()

    elif shop_name.lower() in ["kumej", "kume"]:
        from brands.kume.client import KumeClient

        res = KumeClient()

    elif shop_name.lower() in ["lememek", "lememe"]:
        from brands.lememe.client import LememeClient

        res = LememeClient()

    elif shop_name.lower() == "rohseoul":
        from brands.rohseoul.client import RohseoulClient

        res = RohseoulClient()

    elif shop_name.lower() in ["ssilkr", "ssil"]:
        from brands.ssil.client import SsilClient

        res = SsilClient()

    else:
        cred = credentials(shop_name)
        res = Client(
            shop_name=cred.shop_name,
            access_token=cred.access_token,
            google_credential_path=cred.google_credential_path,
            sheet_id=cred.google_sheet_id,
        )
    return res
