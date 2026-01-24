import datetime
import json
import logging
import pathlib
import pandas as pd
from brands.sanity_checks import SanityChecks
from helpers.client import Client

logger = logging.getLogger(__name__)


class BrandClientBase(Client, SanityChecks):
    SHOPNAME = ""
    VENDOR = ""
    LOCATIONS = []
    PRODUCT_SHEET_START_ROW = 1
    NEW_PRODUCT_TAG = "New Arrival"
    REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = True

    def __init__(self):
        assert self.SHOPNAME, "SHOPNAME must be set in subclass"
        assert self.VENDOR, "VENDOR must be set in subclass"
        assert self.LOCATIONS, "LOCATIONS must be set in subclass"
        from utils import credentials

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
        self.drive_link_cache = {}  # repopulate drive link cache
        return self.to_products_list(
            self.sheet_id,
            sheet_name,
            self.PRODUCT_SHEET_START_ROW,
            product_attr_column_map=self.product_attr_column_map(),
            option1_attr_column_map=self.option1_attr_column_map(),
            option2_attr_column_map=self.option2_attr_column_map(),
            handle_suffix=handle_suffix,
        )

    def get_tags(self, product_info, additional_tags):
        return [self.NEW_PRODUCT_TAG]

    def get_size_field(self, product_info):
        raise NotImplementedError

    def post_product_info_to_product(self, product_info_to_product_res, product_info):
        pass

    def product_info_to_product(self, product_info, additional_tags=None):
        logger.info(f'creating {product_info["title"]}')
        res = self.create_product_and_activate_inventory(
            product_info,
            self.VENDOR,
            description_html=self.get_description_html(product_info),
            tags=self.get_tags(product_info, additional_tags),
            location_names=self.LOCATIONS,
        )
        return self.post_product_info_to_product(res, product_info)

    def segment_options_list_by_key_option(self, option_dicts):
        """
        group the flat options list to list of lists by the same first option i.e. color

        [{'option_values': {'カラー': 'PINK', 'サイズ': '2'}, 'price': 35200, 'sku': 'ALV-90154-PK-2', 'stock': 2},
         {'option_values': {'カラー': 'PINK', 'サイズ': '3'}, 'price': 35200, 'sku': 'ALV-90154-PK-3', 'stock': 2},
         {'option_values': {'カラー': 'PINK', 'サイズ': '4'}, 'price': 35200, 'sku': 'ALV-90154-PK-4', 'stock': 2},
         {'option_values': {'カラー': 'INK BLACK', 'サイズ': '2'}, 'price': 35200, 'sku': 'ALV-90154-BK-2', 'stock': 2},
         {'option_values': {'カラー': 'INK BLACK', 'サイズ': '3'}, 'price': 35200, 'sku': 'ALV-90154-BK-3', 'stock': 2},
         {'option_values': {'カラー': 'INK BLACK', 'サイズ': '4'}, 'price': 35200, 'sku': 'ALV-90154-BK-4', 'stock': 2}]
         becomes

        [[{'option_values': {'カラー': 'PINK', 'サイズ': '2'}, 'price': 35200, 'sku': 'ALV-90154-PK-2', 'stock': 2},
          {'option_values': {'カラー': 'PINK', 'サイズ': '3'}, 'price': 35200, 'sku': 'ALV-90154-PK-3', 'stock': 2},
          {'option_values': {'カラー': 'PINK', 'サイズ': '4'}, 'price': 35200, 'sku': 'ALV-90154-PK-4', 'stock': 2}],
         [{'option_values': {'カラー': 'INK BLACK', 'サイズ': '2'}, 'price': 35200, 'sku': 'ALV-90154-BK-2', 'stock': 2},
          {'option_values': {'カラー': 'INK BLACK', 'サイズ': '3'}, 'price': 35200, 'sku': 'ALV-90154-BK-3', 'stock': 2},
          {'option_values': {'カラー': 'INK BLACK', 'サイズ': '4'}, 'price': 35200, 'sku': 'ALV-90154-BK-4', 'stock': 2}]]
        """
        res = {}
        key_attr = list(option_dicts[0]["option_values"].keys())[0]
        for option in option_dicts:
            res.setdefault(option["option_values"][key_attr], []).append(option)
        return list(res.values())

    def add_variants_from_product_info(self, product_info):
        optionss = self.segment_options_list_by_key_option(
            self.populate_option_dicts(product_info)
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
                option_names=options[0]["option_values"].keys(),
                variant_option_valuess=[
                    option["option_values"].values() for option in options
                ],
                prices=[option["price"] for option in options],
                stocks=[option["stock"] for option in options],
                location_id=self.location_id_by_name(self.LOCATIONS[0]),
            )
        self.enable_and_activate_inventory_by_product_id(
            product_id, location_names=self.LOCATIONS
        )

    def update_stocks(self, product_info_list):
        super().update_stocks(product_info_list, self.LOCATIONS[0])

    def merge_products_as_variants(self, product_title):
        return super().merge_products_as_variants(
            product_title, location_names=self.LOCATIONS
        )

    def sanity_check_sheet(self, sheet_name, handle_suffix=None):
        product_info_list = self.product_info_list_from_sheet(
            sheet_name, handle_suffix=handle_suffix
        )
        logger.info(
            f"Sanity checking {len(product_info_list)} products from sheet {sheet_name}"
        )
        return self.sanity_check_product_info_list(product_info_list)

    def has_open_orders(self, product_title):
        products = self.products_by_title(product_title)
        for product in products:
            for variant in product["variants"]["nodes"]:
                orders = self.orders_by_sku(sku=variant["sku"], open_only=True)
                if orders:
                    return True

    def merge_existing_products_as_variants(self):
        product_titles = self.product_titles_with_multiple_products()
        for product_title in product_titles:
            if self.has_open_orders(product_title):
                logger.info(
                    f"skipping merging products with title {product_title} having open orders"
                )
            else:
                logger.info(f"merging products with title {product_title} as variants")
                self.merge_products_as_variants(product_title)

    def remove_existing_new_proudct_tags(self):
        products = self.products_by_tag(self.NEW_PRODUCT_TAG)
        for product in products:
            logger.info(f"removing {self.NEW_PRODUCT_TAG} tag from {product['title']}")
            tags = [t for t in product["tags"] if t != self.NEW_PRODUCT_TAG]
            self.update_product_tags(product_id=product["id"], tags=",".join(tags))

    def remove_existing_new_badges(self):
        if self.VENDOR in ["blossom", "lememe"]:
            products = self.products_by_metafield("custom", "badges", "NEW")
            for product in products:
                logger.info(
                    f"Removing 'NEW' badge from {product['title']} (id: {product['id']})"
                )
                badges = [
                    m for m in product["metafields"]["nodes"] if m["key"] == "badges"
                ][0]["value"]
                badges = [b for b in json.loads(badges) if b != "NEW"]
                self.update_badges_metafield(product["id"], badges)

    def pre_process_product_info_list_to_products(self, product_info_list):
        if self.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS:
            self.remove_existing_new_proudct_tags()
            self.remove_existing_new_badges()

    def process_product_info_list_to_products(
        self,
        product_info_list,
        additional_tags,
        scheduled_time=None,
        handle_suffix=None,
    ):
        for product_info in product_info_list:
            self.product_info_to_product(product_info, additional_tags=additional_tags)
            self.process_product_images(product_info, handle_suffix=handle_suffix)
        self.update_stocks(product_info_list)
        self.publish_products(product_info_list, scheduled_time=scheduled_time)

    def colors_from_product_info_list(self, product_info_list):
        if "options" in product_info_list[0]:
            for option in ["カラー", "Color"]:
                if option in product_info_list[0]["options"][0].keys():
                    break
            else:
                return False
            return set([o[option] for pi in product_info_list for o in pi["options"]])

    def post_process_product_info_list_to_products(self, product_info_list):
        if colors := self.colors_from_product_info_list(product_info_list):
            current_color_swatch_config = self.current_color_swatch_config()
            configured_colors = [
                l.split(": ")[0] for l in current_color_swatch_config.split("\n")
            ]
            missings = [color for color in colors if color not in configured_colors]
            if missings:
                logger.warning(f"add these colors to color swatch config:")
                for color in missings:
                    print(color)

    def process_sheet_to_products(
        self,
        sheet_name,
        additional_tags=None,
        handle_suffix=None,
        restart_at_product_title=None,
        scheduled_time=None,
        ignore_product_titles=None,
    ):
        product_info_list = self.product_info_list_from_sheet(sheet_name, handle_suffix)
        if not restart_at_product_title:
            i = 0
        else:
            self.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
            if restart_at_product_title == "DO NOT CREATE":
                i = len(product_info_list)
            else:
                for i, pi in enumerate(product_info_list):
                    if pi["title"] == restart_at_product_title:
                        break
                else:
                    raise RuntimeError(
                        f"Product with name {restart_at_product_title} not found in sheet {sheet_name}"
                    )
        product_info_list = [
            pi
            for pi in product_info_list[i:]
            if pi["title"] not in (ignore_product_titles or [])
        ]
        self.pre_process_product_info_list_to_products(product_info_list)
        self.process_product_info_list_to_products(
            product_info_list,
            additional_tags=additional_tags,
            scheduled_time=scheduled_time,
            handle_suffix=handle_suffix,
        )
        self.post_process_product_info_list_to_products(product_info_list)

    def get_skus_from_excel(
        self,
        file_path,
        header_row=None,
        sku_column=1,
        discount_column=None,
    ):
        """
        ExcelファイルからSKUを取得する（オプションで割引率も取得可能）

        Args:
            file_path: Excelファイルのパス（文字列またはpathlib.Path）
            sku_column: SKUが含まれる列のインデックス（0ベース、デフォルト: 1 = B列）
            discount_column: 割引率が含まれる列のインデックス（0ベース、Noneの場合は取得しない）
            header_row: ヘッダー行のインデックス（0ベース、Noneの場合はheader=Noneで読み込む）

        Returns:
            discount_columnがNoneの場合: SKUのリスト
            discount_columnが指定されている場合: (SKU, 割引%)のタプルのリスト
        """
        # pathlib.Pathオブジェクトの場合は文字列に変換
        if isinstance(file_path, pathlib.Path):
            file_path = str(file_path)

        df = pd.read_excel(file_path, header=header_row)

        # 必要な列を取得
        columns_to_get = [sku_column]
        if discount_column is not None:
            columns_to_get.append(discount_column)
        column_names = [df.columns[i] for i in columns_to_get]
        df = df[column_names]
        df = df[df[column_names[0]].notna()]  # SKU列がNaNでない行のみ
        if len(column_names) == 1:
            return df[column_names[0]].tolist()
        return df.values.tolist()


def main():
    from brands.kume.client import KumeClient

    client = KumeClient()
    pairs = client.get_skus_from_excel(
        "/Users/taro/Downloads/(KUME) Japan Shopify Sale List_Outer Sale (1118-1123)_251107.xlsx",
        header_row=3,
        sku_column=1,
        discount_column=6,
    )
    for sku, discount in pairs:
        print(sku, discount)

    for sku in client.get_skus_from_excel(
        "/Users/taro/Downloads/(KUME) Japan Shopify Sale List_Outer Sale (1118-1123)_251107.xlsx",
        header_row=3,
        sku_column=1,
        discount_column=None,
    ):
        print(sku)


if __name__ == "__main__":
    main()
