import json
import logging
import string
from brands.brandclientbase import BrandClientBase

logger = logging.getLogger(__name__)


class SsilClient(BrandClientBase):

    SHOPNAME = "ssilkr"
    VENDOR = "ssil"
    LOCATIONS = ["Shop location"]

    def product_info_list_from_sheet(self, sheet_name):
        start_row = 1
        column_product_attrs = dict(
            title=string.ascii_lowercase.index("a"),
            tags=string.ascii_lowercase.index("b"),
            price=string.ascii_lowercase.index("d"),
            description=string.ascii_lowercase.index("f"),
            product_care=string.ascii_lowercase.index("h"),
            material=string.ascii_lowercase.index("j"),
            size_text=string.ascii_lowercase.index("k"),
            made_in=string.ascii_lowercase.index("l"),
        )
        option1_attrs = {"Color": string.ascii_lowercase.index("m")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("n"),
        )
        option2_attrs = {"Size": string.ascii_lowercase.index("o")}
        option2_attrs.update(
            sku=string.ascii_lowercase.index("p"),
            stock=string.ascii_lowercase.index("q"),
        )
        return self.to_products_list(
            self.sheet_id,
            sheet_name,
            start_row,
            column_product_attrs,
            option1_attrs,
            option2_attrs,
        )

    def sanity_check_product_info_list(self, product_info_list):
        # super().sanity_check_product_info_list(
        #     product_info_list, self.formatted_size_text_to_html_table
        # )
        pass

    def update_metafields(self, product_id, product_info):
        logger.info(f'updating metafields for {product_info["title"]}')
        size_text = self.text_to_simple_richtext(product_info["size_text"])
        product_care = self.text_to_simple_richtext(product_info["product_care"])
        self.update_product_care_metafield(product_id, product_care)
        self.update_product_metafield(
            product_id, "custom", "size_text", json.dumps(size_text)
        )
        material_text = self.text_to_simple_richtext(product_info["material"])
        self.update_product_metafield(
            product_id, "custom", "material_text", json.dumps(material_text)
        )

    def create_a_product(self, product_info):
        logger.info(f'creating {product_info["title"]}')
        description_html = self.get_description(
            product_info["description"],
            product_info["made_in"],
        )
        tags = product_info["tags"]
        res = super().create_a_product(
            product_info, self.VENDOR, description_html, tags, self.LOCATIONS
        )
        product_id = res[0]["id"]
        self.update_metafields(product_id, product_info)
        return product_id

    def get_description(self, product_description, made_in):
        description_html = product_description_template()
        description_html = description_html.replace(
            "${DESCRIPTION}", product_description.replace("\n", "<br>")
        )
        description_html = description_html.replace("${MADEIN}", made_in)
        return description_html


def product_description_template():
    return r"""<!DOCTYPE html>
<html><body>
  <div id="ssilProduct">
    <p>${DESCRIPTION}</p>
    <br>
    <p>原産国: ${MADEIN}</p>
  </div>
</body>
</html>"""
