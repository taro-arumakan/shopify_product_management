import logging
from helpers.shopify_graphql_client import ShopifyGraphqlClient
from helpers.google_api_interface.interface import GoogleApiInterface

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
        self, product_id, drive_id, local_dir, local_prefix, remove_existings=False
    ):
        local_paths = self.drive_images_to_local(drive_id, local_dir, local_prefix)
        res = self.upload_and_assign_images_to_product(
            product_id, local_paths, remove_existings
        )
        return res

    def process_product_images(
        self, product_info, local_dir, local_prefix, handle_suffix=None
    ):
        if handle_suffix:
            product_id = self.product_id_by_handle(
                self.product_title_to_handle(product_info["title"], handle_suffix)
            )
        else:
            product_id = self.product_id_by_title(product_info["title"])
        drive_links, skuss = self.populate_drive_ids_and_skuss(product_info)
        ress = []
        for index, (drive_id, skus) in enumerate(zip(drive_links, skuss)):
            res = self.add_product_images(
                product_id,
                drive_id,
                local_dir,
                local_prefix,
                remove_existings=index == 0,
            )
            ress.append(res)
            variant_media_id = res[-1]["productCreateMedia"]["media"][0]["id"]
            logger.info(f"assigning media {variant_media_id} to {skus}")
            ress.append(self.assign_image_to_skus(product_id, variant_media_id, skus))
        return ress

    def create_a_product(
        self, product_info, vendor, description_html, tags, location_names
    ):
        logger.info(f'creating {product_info["title"]}')
        options = self.populate_option(product_info)
        if options:
            res = self.product_create(
                title=product_info["title"],
                handle=product_info.get("handle"),
                description_html=description_html,
                vendor=vendor,
                tags=tags,
                option_lists=options,
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
        res2 = self._enable_and_activate_inventory(
            product_info, location_names, options
        )
        return (res, res2)

    def _enable_and_activate_inventory(
        self, product_info, location_names, options=None
    ):
        options = options or self.populate_option(product_info)
        skus = [option[2] for option in options] if options else [product_info["sku"]]
        res2 = [self.enable_and_activate_inventory(sku, location_names) for sku in skus]
        return res2
