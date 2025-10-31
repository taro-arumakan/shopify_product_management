import collections
import datetime
import logging
import pathlib
from helpers.shopify_graphql_client import ShopifyGraphqlClient
from helpers.google_api_interface.interface import GoogleApiInterface
from helpers.exceptions import (
    NoVariantsFoundException,
    NoProductsFoundException,
    MultipleProductsFoundException,
)

logger = logging.getLogger(__name__)


class Client(ShopifyGraphqlClient, GoogleApiInterface):
    def __init__(self, shop_name, access_token, google_credential_path, sheet_id=None):
        ShopifyGraphqlClient.__init__(
            self, shop_name=shop_name, access_token=access_token
        )
        GoogleApiInterface.__init__(
            self, google_credential_path=google_credential_path, sheet_id=sheet_id
        )

    def add_product_images(
        self, product_id, drive_id, local_dir, filename_prefix, remove_existings=False
    ):
        local_paths = self.drive_images_to_local(
            drive_id, local_dir, filename_prefix=filename_prefix
        )
        res = self.upload_and_assign_images_to_product(
            product_id, local_paths, remove_existings
        )
        return res

    def process_product_images(
        self, product_info, local_dir=None, filename_prefix=None, handle_suffix=None
    ):
        if handle_suffix:
            product_id = self.product_id_by_handle(
                self.product_title_to_handle(product_info["title"], handle_suffix)
            )
        else:
            product_id = self.product_id_by_title(product_info["title"])

        local_dir = (
            local_dir
            or f"{pathlib.Path.home()}/Downloads/{self.shop_name}_{datetime.date.today():%Y%m%d}/"
        )
        filename_prefix = filename_prefix or f"upload_{datetime.date.today():%Y%m%d}"

        drive_links, skuss = self.populate_drive_ids_and_skuss(product_info)
        ress = []
        for index, (drive_id, skus) in enumerate(zip(drive_links, skuss)):
            res = self.add_product_images(
                product_id,
                drive_id,
                local_dir,
                filename_prefix=f"{filename_prefix}_{skus[0]}",
                remove_existings=index == 0,
            )
            ress.append(res)
            if res[-1]["productCreateMedia"]["media"]:
                variant_media_id = res[-1]["productCreateMedia"]["media"][0]["id"]
                logger.info(f"assigning media {variant_media_id} to {skus}")
                ress.append(
                    self.assign_image_to_skus(product_id, variant_media_id, skus)
                )
            else:
                logger.error(f"\n\n!!! missing images: {skus} !!!\n\n")
        return ress

    def create_product_from_product_info(
        self, product_info, vendor, description_html, tags, location_names
    ):
        logger.info(f'creating {product_info["title"]}')
        options = self.populate_option_dicts(product_info)
        if options:
            res = self.product_create(
                title=product_info["title"],
                handle=product_info.get("handle"),
                description_html=description_html,
                vendor=vendor,
                tags=tags,
                option_dicts=options,
            )
        else:
            res = self.product_create_default_variant(
                title=product_info["title"],
                description_html=description_html,
                handle=product_info.get("handle"),
                vendor=vendor,
                tags=tags,
                price=product_info["price"],
                sku=product_info["sku"],
            )
        logger.info(f"activating inventory")
        res2 = self.enable_and_activate_inventory_by_product_info(
            product_info, location_names
        )
        return (res, res2)

    def enable_and_activate_inventory_by_product_info(
        self, product_info, location_names
    ):
        skus = self.product_info_to_skus(product_info)
        res = [
            self.enable_and_activate_inventory_by_sku(sku, location_names)
            for sku in skus
        ]
        return res

    def get_sku_stocks_map(self, product_info):
        variants_info = self.get_variants_level_info(product_info)
        return {variant["sku"]: variant.get("stock", 0) for variant in variants_info}

    def update_stocks(self, product_info_list, location_name):
        logger.info("updating inventory")
        location_id = self.location_id_by_name(location_name)
        sku_stock_map = {}
        [
            sku_stock_map.update(self.get_sku_stocks_map(product_info))
            for product_info in product_info_list
        ]
        return [
            self.set_inventory_quantity_by_sku_and_location_id(sku, location_id, stock)
            for sku, stock in sku_stock_map.items()
        ]

    def publish_products(self, product_info_list, scheduled_time=None):
        for pi in product_info_list:
            product_id = self.product_id_by_title(pi["title"])
            self.activate_and_publish_by_product_id(
                product_id, scheduled_time=scheduled_time
            )

    def replace_images_by_skus(
        self, skus, folder_id, local_dir=None, filename_prefix=None
    ):
        medias = self.medias_by_sku(skus[0])
        existing_ids = [m["id"] for m in medias]
        logger.info(f"going to replace images of {skus} with {folder_id}")

        local_dir = (
            local_dir
            or f"{pathlib.Path.home()}/Downloads/{self.shop_name}_{datetime.date.today():%Y%m%d}/"
        )
        filename_prefix = (
            filename_prefix or f"upload_{datetime.date.today():%Y%m%d}_{skus[0]}"
        )

        local_paths = self.drive_images_to_local(
            folder_id,
            local_dir,
            filename_prefix=filename_prefix,
        )
        file_names = [path.rsplit("/", 1)[-1] for path in local_paths]
        mime_types = [f"image/{path.rsplit('.', 1)[-1]}" for path in local_paths]
        staged_targets = self.generate_staged_upload_targets(file_names, mime_types)
        logger.info(f"generated staged upload targets: {len(staged_targets)}")
        self.upload_images_to_shopify_parallel(staged_targets, local_paths, mime_types)

        product_id = self.product_id_by_sku(skus[0])
        logger.info(
            f"Images uploaded for {product_id}, going to remove existing and assign."
        )
        if medias:
            logger.info(f"removing media ids: {existing_ids}")
            self.remove_product_media_by_product_id(product_id, existing_ids)
        logger.info(f"adding medias to {product_id}")
        self.assign_images_to_product(
            [target["resourceUrl"] for target in staged_targets],
            alts=file_names,
            product_id=product_id,
        )
        logger.info(f"adding a media to {skus}")
        uploaded_variant_media = self.media_by_product_id_by_file_name(
            product_id, file_names[0]
        )
        self.assign_image_to_skus(product_id, uploaded_variant_media["id"], skus)

    def check_size_texts(
        self, product_info_list, text_to_html_func=None, raise_on_error=True
    ):
        res = []
        for product_info in product_info_list:
            try:
                if hasattr(self, "get_size_field"):
                    size_text = self.get_size_field(product_info)
                else:
                    text_to_html_func(product_info["size_text"])
            except Exception as e:
                m = f"Error formatting size text for {product_info['title']}: {e}"
                if raise_on_error:
                    logger.error(m)
                    raise
                else:
                    res.append(m)
            else:
                if raise_on_error:
                    print(size_text)
        if not raise_on_error:
            return res

    def product_info_to_skus(self, product_info):
        options = self.populate_option_dicts(product_info)
        return [o["sku"] for o in options]

    def check_sku_duplicates(self, product_info_list):
        skus = sum([self.product_info_to_skus(pi) for pi in product_info_list], [])
        counts_by_sku = collections.Counter(skus)
        counts_by_sku = {
            sku: count for sku, count in counts_by_sku.items() if count > 1
        }
        if counts_by_sku:
            raise RuntimeError(
                f"Duplicate SKUs found:\n{'\n'.join(": ".join(map(str, [sku, count])) for sku, count in counts_by_sku.items())}"
            )

    def check_existing_skus(self, product_info_list):
        res = []
        for pi in product_info_list:
            skus = self.product_info_to_skus(pi)
            for sku in skus:
                try:
                    self.variant_by_sku(sku)
                except NoVariantsFoundException:
                    pass
                else:
                    res.append(f"Existing SKU found: {pi['title']} - {sku}")
        return res

    def check_existing_products(self, product_info_list):
        res = []
        for pi in product_info_list:
            try:
                checking = "handle" if "handle" in pi else "title"
                func = getattr(self, f"product_by_{checking}")
                param = pi[checking]
                func(param)
            except NoProductsFoundException:
                pass
            except MultipleProductsFoundException:
                res.append(f"Existing product found by {checking}: {param}")
            else:
                res.append(f"Existing product found by {checking}: {param}")
        return res

    def sanity_check_product_info_list(self, product_info_list, text_to_html_func=None):
        res = []
        try:
            self.check_sku_duplicates(product_info_list)
        except RuntimeError as e1:
            logger.error(e1)
            res.append(e1)
        res = self.check_existing_skus(product_info_list)
        res += self.check_existing_products(product_info_list)
        res += self.check_size_texts(
            product_info_list, text_to_html_func, raise_on_error=False
        )
        for r in res:
            logger.error(r)

        if res:
            raise RuntimeError("Failed sanity check")
