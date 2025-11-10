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
            product_care=string.ascii_lowercase.index("g"),
            material=string.ascii_lowercase.index("h"),
            size_text=string.ascii_lowercase.index("i"),
            made_in=string.ascii_lowercase.index("j"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"Color": string.ascii_lowercase.index("k")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("l"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        option2_attrs = {"Size": string.ascii_lowercase.index("m")}
        option2_attrs.update(
            sku=string.ascii_lowercase.index("n"),
            stock=string.ascii_lowercase.index("o"),
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
            "${MADEIN}", product_info.get("made_in", "KOREA")
        )
        return description_html

    def get_tags(self, product_info, additional_tags=None):
        return ",".join([product_info["tags"]] + (additional_tags or []))

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
        if size_table_html := self.get_size_field(product_info):
            self.update_product_metafield(
                product_id, "custom", "size_table_html", size_table_html
            )
        self.update_badges_metafield(product_id, ["NEW"])
        if product_care := product_info.get("product_care", "").strip():
            self.update_product_care_metafield(
                product_id, self.text_to_simple_richtext(product_care)
            )


class BlossomClientClothes(BlossomClient):
    pass


class BlossomClientShoes(BlossomClient):
    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("b"),
            tags=string.ascii_lowercase.index("c"),
            price=string.ascii_lowercase.index("e"),
            description=string.ascii_lowercase.index("g"),
            product_care=string.ascii_lowercase.index("i"),
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


class BlossomClientBags(BlossomClient):
    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("b"),
            tags=string.ascii_lowercase.index("c"),
            price=string.ascii_lowercase.index("e"),
            description=string.ascii_lowercase.index("g"),
            product_care=string.ascii_lowercase.index("i"),
            material=string.ascii_lowercase.index("j"),
            size_text=string.ascii_lowercase.index("k"),
            made_in=string.ascii_lowercase.index("l"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"Color": string.ascii_lowercase.index("m")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("n"),
            sku=string.ascii_lowercase.index("o"),
            stock=string.ascii_lowercase.index("p"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        return {}

    def remove_new_badge_from_existing_products(self):
        logger.info("Removing 'NEW' badge from existing products")
        products = self.products_by_metafield("custom", "badges", "NEW")
        for product in products:
            logger.info(f"Removing 'NEW' badge from {product['title']} (id: {product['id']})")
            self.update_badges_metafield(product["id"], [])

    def process_sheet_to_products(
        self,
        sheet_name,
        additional_tags=None,
        handle_suffix=None,
        restart_at_product_name=None,
        scheduled_time=None,
        remove_new_badge=True,
    ):
        # remove'NEW'badge
        if remove_new_badge:
            self.remove_new_badge_from_existing_products()

        super().process_sheet_to_products(
            sheet_name,
            additional_tags=additional_tags,
            handle_suffix=handle_suffix,
            restart_at_product_name=restart_at_product_name,
            scheduled_time=scheduled_time,
        )



def main():
    client = BlossomClient()
    client.sanity_check_sheet("clothes(drop4)")


if __name__ == "__main__":
    main()
