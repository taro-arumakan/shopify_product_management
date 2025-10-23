import json
import logging
import string
from brands.brandclientbase import BrandClientBase

logger = logging.getLogger(__name__)


class SsilClient(BrandClientBase):

    SHOPNAME = "ssilkr"
    VENDOR = "ssil"
    LOCATIONS = ["Shop location"]
    PRODUCT_SHEET_START_ROW = 1

    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("a"),
            tags=string.ascii_lowercase.index("b"),
            price=string.ascii_lowercase.index("d"),
            description=string.ascii_lowercase.index("f"),
            product_care=string.ascii_lowercase.index("h"),
            material=string.ascii_lowercase.index("j"),
            size_text=string.ascii_lowercase.index("k"),
            made_in=string.ascii_lowercase.index("l"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"Color": string.ascii_lowercase.index("m")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("n"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        option2_attrs = {"Size": string.ascii_lowercase.index("o")}
        option2_attrs.update(
            sku=string.ascii_lowercase.index("p"),
            stock=string.ascii_lowercase.index("q"),
        )
        return option2_attrs

    def sanity_check_product_info_list(self, product_info_list):
        # super().sanity_check_product_info_list(
        #     product_info_list, self.formatted_size_text_to_html_table
        # )
        pass

    def get_description_html(self, product_info):
        description_html = product_description_template()
        description_html = description_html.replace(
            "${DESCRIPTION}", product_info["description"].replace("\n", "<br>")
        )
        description_html = description_html.replace(
            "${MADEIN}", product_info["made_in"]
        )
        return description_html

    def get_tags(self, product_info):
        return product_info["tags"]

    def post_create_a_product(self, create_a_product_res, product_info):
        product_id = create_a_product_res[0]["id"]
        self.update_metafields(product_id, product_info)
        return product_id

    def update_metafields(self, product_id, product_info):
        logger.info(f'updating metafields for {product_info["title"]}')
        if size_text := product_info.get("size_text"):
            size_text = self.text_to_simple_richtext(size_text)
            self.update_product_metafield(
                product_id, "custom", "size_text", json.dumps(size_text)
            )
        else:
            logger.warning(f"no size_text for {product_info['title']}")
        product_care = self.text_to_simple_richtext(product_info["product_care"])
        self.update_product_care_metafield(product_id, product_care)
        material_text = self.text_to_simple_richtext(product_info["material"])
        self.update_product_metafield(
            product_id, "custom", "material_text", json.dumps(material_text)
        )


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
