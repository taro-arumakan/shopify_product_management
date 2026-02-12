import io
import logging
import requests
import zipfile
from helpers.dropbox_utils import format_download_link

logger = logging.getLogger(__name__)


class ApricotStudiosSanityChecks:

    def check_description(self, product_inputs, raise_on_error=True):
        logger.info("Checking descriptions")
        res = []
        for product_input in product_inputs:
            try:
                description_html = self.get_product_description_richtext(product_input)
            except Exception as e:
                m = f"Error formatting description for {product_input['title']}: {e}"
                if raise_on_error:
                    logger.error(m)
                    raise
                else:
                    res.append(m)
            else:
                if raise_on_error:
                    print(description_html)
        return res

    def list_dropbox_link_files(self, shared_link):
        res = requests.get(format_download_link(shared_link))
        with zipfile.ZipFile(io.BytesIO(res.content)) as z:
            names = z.namelist()
        return [name for name in names if "/" not in name]

    def check_product_main_image_links(self, product_inputs):
        logger.info("Checking main image links")
        res = []
        for product_input in product_inputs:
            logger.debug(f"Checking image links for {product_input['title']}")
            try:
                if not self.list_dropbox_link_files(
                    product_input["product_main_images_link"]
                ):
                    res.append(
                        f"Invalid product main image for {product_input['title']}"
                    )
            except KeyError:
                res.append(f"No product main image link for {product_input['title']}")
        return res

    def check_variant_image_links(self, product_inputs):
        logger.info("Checking variant image links")
        res = []
        for product_input in product_inputs:
            for variant in product_input["options"]:
                try:
                    if not self.list_dropbox_link_files(variant["variant_images_link"]):
                        res.append(
                            f"Invalid variant image for {product_input['product_main_images']} - {variant['カラー']}"
                        )
                except KeyError:
                    res.append(
                        f"No variant image link for {product_input['title']} - {variant['カラー']}"
                    )
        return res

    def check_product_details_image_links(self, product_inputs):
        logger.info("Checking product details image links")
        res = []
        for product_input in product_inputs:
            folder_name = product_input["title"]
            drive_id = self.find_folder_id_by_name(
                self.product_detail_images_folder_id, folder_name
            )
            image_details = self.get_drive_image_details(drive_id)
            if not image_details:
                res.append(
                    f"Missing or inaccessible drive image for {product_input['title']}: {drive_id}"
                )
        return res

    def check_images_link(self, product_inputs):
        logger.info("Checking image links")
        res = self.check_product_main_image_links(product_inputs)
        res += self.check_variant_image_links(product_inputs)
        res += self.check_product_details_image_links(product_inputs)
        return res
