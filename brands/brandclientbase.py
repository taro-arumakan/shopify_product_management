import datetime
import logging
import pathlib
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

    def get_tags(self, product_info):
        raise NotImplementedError

    def get_size_field(self, product_info):
        raise NotImplementedError

    def post_create_a_product(self, create_a_product_res, product_info):
        pass

    def create_product_from_product_info(self, product_info):
        logger.info(f'creating {product_info["title"]}')
        create_a_product_res = super().create_product_from_product_info(
            product_info,
            self.VENDOR,
            description_html=self.get_description_html(product_info),
            tags=self.get_tags(product_info),
            location_names=self.LOCATIONS,
        )
        return self.post_create_a_product(create_a_product_res, product_info)

    def segment_options_list_by_key_option(self, options):
        """
        group the flat options list to list of lists by the same first option i.e. color

        [[{'カラー': 'KHAKI BROWN', 'サイズ': 'S'}, 18260, 'APB3PT030KBS', 3],
         [{'カラー': 'KHAKI BROWN', 'サイズ': 'M'}, 18260, 'APB3PT030KBM', 3],
         [{'カラー': 'BLACK', 'サイズ': 'S'}, 18260, 'APB3PT030BKS', 3],
         [{'カラー': 'BLACK', 'サイズ': 'M'}, 18260, 'APB3PT030BKM', 3]]

         becomes

        [[[{'カラー': 'KHAKI BROWN', 'サイズ': 'S'}, 18260, 'APB3PT030KBS', 3],
          [{'カラー': 'KHAKI BROWN', 'サイズ': 'M'}, 18260, 'APB3PT030KBM', 3]],
         [[{'カラー': 'BLACK', 'サイズ': 'S'}, 18260, 'APB3PT030BKS', 3],
          [{'カラー': 'BLACK', 'サイズ': 'M'}, 18260, 'APB3PT030BKM', 3]]]
        """
        res = {}
        key_attr = list(options[0][0].keys())[0]
        for option in options:
            res.setdefault(option[0][key_attr], []).append(option)
        return list(res.values())

    def add_variants_from_product_info(self, product_info):
        optionss = self.segment_options_list_by_key_option(
            self.populate_option(product_info)
        )
        drive_links, skuss = self.populate_drive_ids_and_skuss(product_info)
        product_id = self.product_id_by_title(product_info["title"])
        for drive_link, skus, options in zip(drive_links, skuss, optionss):
            logger.info(f"  processing sku: {skus} - {drive_link}")
            res = self.add_product_images(
                product_id,
                drive_link,
                f"{pathlib.Path.home()}/Downloads/gbh{datetime.date.today():%Y%m%d}/",
                f"upload_{datetime.date.today():%Y%m%d}_{skus[0]}_",
            )
            new_media_ids = [m["id"] for m in res[-1]["productCreateMedia"]["media"]]
            self.variants_add(
                product_id=product_id,
                skus=skus,
                media_ids=[],
                variant_media_ids=[new_media_ids[0]],
                option_names=options[0][0].keys(),
                variant_option_valuess=[option[0].values() for option in options],
                prices=[option[1] for option in options],
                stocks=[option[3] for option in options],
                location_id=self.location_id_by_name(self.LOCATIONS[0]),
            )
        self.enable_and_activate_inventory_by_product_id(
            product_id, location_names=self.LOCATIONS
        )

    def update_stocks(self, product_info_list):
        super().update_stocks(product_info_list, self.LOCATIONS[0])

    def sanity_check_sheet(
        self, sheet_name, handle_suffix=None, text_to_html_func=None
    ):
        product_info_list = self.product_info_list_from_sheet(
            sheet_name, handle_suffix=handle_suffix
        )
        logger.info(
            f"Sanity checking {len(product_info_list)} products from sheet {sheet_name}"
        )
        return self.sanity_check_product_info_list(
            product_info_list,
            text_to_html_func=text_to_html_func
            or self.formatted_size_text_to_html_table,
        )

    def process_sheet_to_products(
        self, sheet_name, handle_suffix=None, restart_at_product_name=None
    ):
        product_info_list = self.product_info_list_from_sheet(sheet_name, handle_suffix)
        if restart_at_product_name == "DO NOT CREATE":
            i = len(product_info_list)
        elif not restart_at_product_name:
            i = 0
        else:
            for i, pi in enumerate(product_info_list):
                if pi["title"] == restart_at_product_name:
                    break

        for product_info in product_info_list[i:]:
            self.create_product_from_product_info(product_info)
            self.process_product_images(product_info)
        self.update_stocks(product_info_list)
        self.publish_products(product_info_list)
