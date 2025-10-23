import logging
from helpers.client import Client
from utils import credentials

logger = logging.getLogger(__name__)


class BrandClientBase(Client):
    SHOPNAME = ""
    VENDOR = ""
    LOCATIONS = []
    PRODUCT_SHEET_START_ROW = 1

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

    def product_attr_column_map(self):
        raise NotImplementedError

    def option1_attr_column_map(self):
        raise NotImplementedError

    def option2_attr_column_map(self):
        raise NotImplementedError

    def product_info_list_from_sheet(self, sheet_name, handle_suffix=None):
        return self.to_products_list(
            self.sheet_id,
            sheet_name,
            self.PRODUCT_SHEET_START_ROW,
            product_attr_column_map=self.product_attr_column_map(),
            option1_attr_column_map=self.option1_attr_column_map(),
            option2_attr_column_map=self.option2_attr_column_map(),
            handle_suffix=handle_suffix,
        )

    def get_description_html(self, product_info):
        raise NotImplementedError

    def get_tags(self, product_info):
        raise NotImplementedError

    def post_create_a_product(self, create_a_product_res, product_info):
        pass

    def create_a_product(self, product_info):
        logger.info(f'creating {product_info["title"]}')
        create_a_product_res = super().create_a_product(
            product_info,
            self.VENDOR,
            description_html=self.get_description_html(product_info),
            tags=self.get_tags(product_info),
            location_names=self.LOCATIONS,
        )
        return self.post_create_a_product(create_a_product_res, product_info)

    def update_stocks(self, product_info_list):
        super().update_stocks(product_info_list, self.LOCATIONS[0])

    def sanity_check_sheet(self, sheet_name, handle_suffix=None):
        product_info_list = self.product_info_list_from_sheet(
            sheet_name, handle_suffix=handle_suffix
        )
        logger.info(
            f"Sanity checking {len(product_info_list)} products from sheet {sheet_name}"
        )
        return self.sanity_check_product_info_list(product_info_list)
