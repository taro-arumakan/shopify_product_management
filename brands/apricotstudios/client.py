import datetime
import logging
import os
import re
import pathlib
import string
import textwrap
from brands.client.brandclientbase import BrandClientBase
from helpers.dropbox_utils import download_and_rename_images_from_dropbox

logger = logging.getLogger(__name__)


class ApricotStudiosClient(BrandClientBase):

    SHOPNAME = "apricot-studios"
    VENDOR = "Apricot Studios"
    LOCATIONS = ["Apricot Studios Warehouse"]
    PRODUCT_SHEET_START_ROW = 1

    def __init__(self, dummy_product_id="", product_detail_images_folder_id=""):
        """
        dummy_product_id: a dummy product which holds product detail images
        product_detail_images_folder_id: Google Drive folder id where translated product detail images are stored by title
        """
        self.dummy_product_id = dummy_product_id
        self.product_detail_images_folder_id = product_detail_images_folder_id
        if not all((self.dummy_product_id, self.product_detail_images_folder_id)):
            logger.warning(
                "dummy proudct id and product detail images folder id are required for product creation"
            )
        super().__init__()

    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("f"),
            collection=string.ascii_lowercase.index("c"),
            category=string.ascii_lowercase.index("d"),
            release_date=string.ascii_lowercase.index("b"),
            description=string.ascii_lowercase.index("j"),
            material=string.ascii_lowercase.index("n"),
            size_text=string.ascii_lowercase.index("p"),
            made_in=string.ascii_lowercase.index("q"),
            product_main_images_link=string.ascii_lowercase.index("r"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"カラー": string.ascii_lowercase.index("u")}
        option1_attrs.update(
            variant_images_link=string.ascii_lowercase.index("t"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        option2_attrs = {"サイズ": string.ascii_lowercase.index("v")}
        option2_attrs.update(
            price=string.ascii_lowercase.index("h"),
            sku=string.ascii_lowercase.index("w"),
            stock=string.ascii_lowercase.index("y"),
        )
        return option2_attrs

    def get_description_html(self, product_input):
        """
        Apricot Studios holds medias in the description field.
        Description texts are in the metafields.
        """
        return ""

    def get_tags(self, product_input, additional_tags=None):
        return ",".join(
            [
                product_input["collection"],
                product_input["category"],
                product_input["release_date"],
            ]
            + super().get_tags(product_input, additional_tags)
            + (additional_tags or [])
        )

    def get_size_field(self, product_input):
        size_text = product_input.get("size_text")
        if size_text:
            return self.text_to_html_tables_and_paragraphs(size_text)
        else:
            logging.warning(f"No size information found for {product_input['title']}")

    def download_images(self, dirpath: str, images_link, prefix, tempdir):
        if os.path.exists(dirpath):
            return [
                os.path.join(dirpath, p)
                for p in sorted(os.listdir(dirpath))
                if p.endswith((".jpg", ".jpeg", ".png"))
            ]

        return download_and_rename_images_from_dropbox(
            dirpath,
            images_link,
            prefix=prefix,
            tempdir=tempdir,
        )

    def process_product_images(self, product_input):
        """
        As Apricot Studios has their images in Dropbox and also its images structure differs from other brands,
        keeping this customized processing logic.
        """
        logging.info("downloading product main images")
        images_local_dir = f"{pathlib.Path.home()}/Downloads/apricotstudios_{datetime.date.today():%Y%m%d}/"

        image_pathss = [
            self.download_images(
                os.path.join(
                    images_local_dir, product_input["title"], "product_main_images"
                ),
                product_input["product_main_images_link"],
                prefix=f"{self.shopify_compatible_name(product_input['title'])}_product_main",
                tempdir=os.path.join(images_local_dir, "temp"),
            )
        ]
        skuss = []
        for variant in product_input["options"]:
            skus = [o2["sku"] for o2 in variant["options"]]
            logging.info(f"downloading product variant images for skus {skus}")
            image_pathss += [
                self.download_images(
                    os.path.join(
                        images_local_dir,
                        product_input["title"],
                        "variant_images",
                        skus[0],
                    ),
                    variant["variant_images_link"],
                    skus[0],
                    tempdir=os.path.join(images_local_dir, "temp"),
                )
            ]
            skuss.append(skus)

        product_id = self.product_id_by_title(product_input["title"])
        image_position = len(image_pathss[0])
        self.upload_and_assign_images_to_product(product_id, sum(image_pathss, []))
        for variant_image_paths, skus in zip(image_pathss[1:], skuss):
            if image_position < len(sum(image_pathss, [])):
                print(f"assigning variant image at position {image_position} to {skus}")
                self.assign_image_to_skus_by_position(product_id, image_position, skus)
            else:
                print(
                    f"!!! {product_input['title']} - {skus} no image position to assign, skipping"
                )
            image_position += len(variant_image_paths)

        logger.info(f"downloading product detail images")
        folder_name = product_input["title"]
        folder_id = self.find_folder_id_by_name(
            self.product_detail_images_folder_id, folder_name
        )
        detail_image_paths = self.drive_images_to_local(
            folder_id,
            os.path.join(
                images_local_dir, product_input["title"], "product_detail_images"
            ),
            filename_prefix=f"{self.shopify_compatible_name(product_input['title'])}_product_detail",
        )
        self.upload_and_assign_description_images_to_shopify(
            product_id,
            detail_image_paths,
            self.dummy_product_id,
            "https://cdn.shopify.com/s/files/1/0745/9435/3408",
        )

    def post_process_product_input(self, product_input_to_product_res, product_input):
        product_id = product_input_to_product_res[0]["id"]
        self.update_metafields(product_id, product_input)
        return product_id

    def update_metafields(self, product_id, product_input):
        logger.info(f'updating metafields for {product_input["title"]}')
        desc = product_input["description"]
        material = product_input["material"]
        origin = product_input["made_in"]
        product_description = {
            "type": "root",
            "children": [
                {
                    "children": [{"type": "text", "value": desc.strip('"')}],
                    "type": "paragraph",
                },
                {"children": [{"type": "text", "value": ""}], "type": "paragraph"},
                {
                    "children": [{"type": "text", "value": "素材"}],
                    "level": 5,
                    "type": "heading",
                },
                {
                    "children": [{"type": "text", "value": material.strip('"')}],
                    "type": "paragraph",
                },
                {
                    "children": [{"type": "text", "value": "原産国"}],
                    "level": 5,
                    "type": "heading",
                },
                {
                    "children": [{"type": "text", "value": origin.strip('"')}],
                    "type": "paragraph",
                },
            ],
        }
        self.update_product_description_metafield(product_id, product_description)
        if size_table_html := self.get_size_field(product_input):
            self.update_size_table_html_metafield(
                product_id, "custom", "size_text", size_table_html
            )
        self.update_description_include_metafield_values(product_id)

    def update_description_include_metafield_values(self, product_id):
        """hidden description text in the description field for product feed to Meta and Google"""
        fb_sync_description_element = "fb_sync:product_description"

        description_html = self.product_description_by_product_id(product_id)
        metafield_product_description = self.product_metafield_value_by_product_id(
            product_id, "custom", "product_description"
        )
        metafield_product_description_converted = self.convert_rich_text_to_html(
            metafield_product_description
        )
        try:
            metafield_size_table_html = self.product_metafield_value_by_product_id(
                product_id, "custom", "size_table_html"
            )
        except TypeError:
            metafield_size_table_html = ""

        # remove the description text first then repopulate.
        description_html = re.sub(
            f"<{fb_sync_description_element}>.*</{fb_sync_description_element}>",
            "",
            description_html,
            flags=re.DOTALL,
        )
        updated_description = description_html
        updated_description += f"\n\n<{fb_sync_description_element}>"
        updated_description += f"\n{metafield_product_description_converted}"
        if metafield_size_table_html:
            updated_description += f"\n<h5>サイズ</h5>\n{metafield_size_table_html}"
        updated_description += f"\n</{fb_sync_description_element}>"
        return self.update_product_description(product_id, updated_description)

    """ Size table html methods """

    def is_title(self, line):
        if len(line.split("/")) < 2:
            return True

    def is_header(self, parts):
        if parts[0] in ["XS", "S", "M", "L", "XL", "XXL", "6M", "12M", "18M", "24M"]:
            return False
        try:
            float(parts[0])
            return False
        except ValueError:
            return True

    def parse_table_text_to_html(self, table_text):
        lines = map(str.strip, filter(None, table_text.split("\n")))
        titles = []
        tables = []
        headers = []
        rowss = []
        for line in lines:
            if self.is_title(line):
                titles.append(line)
            else:
                parts = re.split(r"[\s/:：]+", line)
                if self.is_header(parts):
                    headers.append([""] + list(map(str.strip, parts)))
                    rowss.append([])
                else:
                    rowss[-1].append(map(str.strip, parts))
        for header, rows in zip(headers, rowss):
            tables.append(self.generate_table_html(header, rows))
        if len(titles) == len(tables):
            tables = [
                f"<h3>{title}</h3>{table}" for title, table in zip(titles, tables)
            ]
        return tables

    def text_to_html_tables_and_paragraphs(self, size_text):
        size_text = (
            size_text.replace("　", " ").replace("\u2003", " ").replace("\u3000", " ")
        )
        if "注意事項" in size_text:
            table_text, notes_text = size_text.split("注意事項", 1)
        elif "ウォーターバッグ" in size_text:
            return f"<p>{size_text}</p>"
        else:
            table_text = size_text
            notes_text = ""
        size_table_htmls = self.parse_table_text_to_html(table_text)
        paragraphs = (
            [p.strip() for p in notes_text.split("\n") if p.strip()]
            if notes_text
            else []
        )

        html_output = "<br>\n<br>\n".join(size_table_htmls)
        for paragraph in paragraphs:
            paragraph = paragraph.split()
            if paragraph:
                html_output += f"<p>{' '.join(paragraph)}</p>\n"
        return html_output


def main():
    client = ApricotStudiosClient(
        "gid://shopify/Product/9181957095680", "1jOg_no7MS8tGwMLKvOpodPg58nWKXSgX"
    )
    for pi in client.product_inputs_by_sheet_name("11.20 25Winter_clone"):
        print(pi["title"], client.get_tags(pi))


if __name__ == "__main__":
    main()
