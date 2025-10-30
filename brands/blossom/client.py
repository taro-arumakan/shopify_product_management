import json
import logging
import re
import string
import textwrap
from brands.brandclientbase import BrandClientBase

logger = logging.getLogger(__name__)


class BlossomClient(BrandClientBase):

    SHOPNAME = "blossomhcompany"
    VENDOR = "blossom"
    LOCATIONS = ["Blossom Warehouse"]
    PRODUCT_SHEET_START_ROW = 1

    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("a"),
            tags=string.ascii_lowercase.index("b"),
            price=string.ascii_lowercase.index("d"),
            description=string.ascii_lowercase.index("f"),
            product_care=string.ascii_lowercase.index("h"),
            material=string.ascii_lowercase.index("i"),
            size_text=string.ascii_lowercase.index("j"),
            made_in=string.ascii_lowercase.index("k"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"Color": string.ascii_lowercase.index("l")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("m"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        option2_attrs = {"Size": string.ascii_lowercase.index("n")}
        option2_attrs.update(
            sku=string.ascii_lowercase.index("o"),
            stock=string.ascii_lowercase.index("p"),
        )
        return option2_attrs

    @staticmethod
    def product_description_template():
        res = r"""
            <!DOCTYPE html>
            <html><body>
            <div id="alvanaProduct">
                <p>${DESCRIPTION}</p>
                <br>
                <table width="100%">
                <tbody>
                    <tr>
                    <td>素材</td>
                    <td>${MATERIAL}</td>
                    </tr>
                    <tr>
                    <td>原産国</td>
                    <td>${MADEIN}</td>
                    </tr>
                </tbody>
                </table>
            </div>
            </body>
            </html>"""
        return textwrap.dedent(res)

    def get_description_html(self, product_info):
        description_html = self.product_description_template()
        description_html = description_html.replace(
            "${DESCRIPTION}", product_info["description"].replace("\n", "<br>")
        )
        description_html = description_html.replace(
            "${MATERIAL}", product_info["material"]
        )
        description_html = description_html.replace(
            "${MADEIN}", product_info["made_in"]
        )
        return description_html

    def get_tags(self, product_info):
        return product_info["tags"] + ["New Arrival"]

    def get_size_field(self, product_info):
        if size_text := product_info.get("size_text"):
            return self.formatted_size_text_to_html_table(size_text)
        else:
            logger.warning(f"no size_text for {product_info['title']}")

    def post_create_product_from_product_info(
        self, create_product_from_product_info_res, product_info
    ):
        product_id = create_product_from_product_info_res[0]["id"]
        self.update_metafields(product_id, product_info)
        return product_id

    def update_metafields(self, product_id, product_info):
        logger.info(f'updating metafields for {product_info["title"]}')
        if size_text := self.get_size_field(product_info):
            self.update_product_metafield(product_id, "custom", "size_text", size_text)
        if product_care := product_info.get("product_care", "").strip():
            self.update_product_care_metafield(
                product_id, self.text_to_simple_richtext(product_care)
            )


class BlossomClientClothes(BlossomClient):
    pass


class BlossomClientShoes(BlossomClient):
    pass


def main():
    client = BlossomClient()
    client.sanity_check_sheet("clothes(drop4)")


if __name__ == "__main__":
    main()
