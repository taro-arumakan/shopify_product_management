from helpers.client import Client
from utils import credentials


class BrandClientBase(Client):
    SHOPNAME = ""
    VENDOR = ""
    LOCATIONS = []

    def __init__(self):
        assert self.SHOPNAME, "SHOPNAME must be set in subclass"
        assert self.VENDOR, "VENDOR must be set in subclass"
        assert self.LOCATIONS, "LOCATIONS must be set in subclass"
        cred = credentials(self.SHOPNAME)
        super().__init__(
            shop_name=cred.shop_name,
            access_token=cred.access_token,
            google_credential_path=cred.google_credential_path,
            sheet_id=cred.google_sheet_id,
        )

    def create_a_product(self, product_info, description_html, tags):
        return super().create_a_product(
            product_info, self.VENDOR, description_html, tags, self.LOCATIONS
        )

    def update_stocks(self, product_info_list):
        super().update_stocks(product_info_list, self.LOCATIONS[0])
