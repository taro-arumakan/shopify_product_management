import logging
import string
import textwrap
from brands.brandclientbase import BrandClientBase


logger = logging.getLogger(__name__)


class AlvanaClient(BrandClientBase):

    SHOPNAME = "alvanas"
    VENDOR = "alvana"
    LOCATIONS = ["Jingumae"]
    PRODUCT_SHEET_START_ROW = 1
    REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False

    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("b"),
            tags=string.ascii_lowercase.index("d"),
            price=string.ascii_lowercase.index("e"),
            description=string.ascii_lowercase.index("f"),
            product_care=string.ascii_lowercase.index("g"),
            material=string.ascii_lowercase.index("h"),
            size_text=string.ascii_lowercase.index("i"),
            weight=string.ascii_lowercase.index("j"),
            made_in=string.ascii_lowercase.index("k"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"カラー": string.ascii_lowercase.index("l")}
        option1_attrs.update(
            filter_color=string.ascii_lowercase.index("m"),
            drive_link=string.ascii_lowercase.index("n"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        option2_attrs = {"サイズ": string.ascii_lowercase.index("o")}
        option2_attrs.update(
            sku=string.ascii_lowercase.index("p"),
            stock=string.ascii_lowercase.index("q"),
        )
        return option2_attrs

    @staticmethod
    def product_description_template():
        res = r"""
            <div id="alvanaProduct">
                <p>${DESCRIPTION}</p>
                <br>
                <table width="100%">
                <tbody>
                    <tr>
                    <th>素材</th>
                    <td>${MATERIAL}</td>
                    </tr>
                    <tr>
                    <th>原産国</th>
                    <td>${MADEIN}</td>
                    </tr>
                </tbody>
                </table>
            </div>
            """
        return textwrap.dedent(res)

    def get_description_html(self, product_input):
        description_html = self.product_description_template()
        description_html = description_html.replace(
            "${DESCRIPTION}", product_input["description"].replace("\n", "<br>")
        )
        description_html = description_html.replace(
            "${MATERIAL}", product_input["material"]
        )
        description_html = description_html.replace(
            "${MADEIN}", product_input["made_in"]
        )
        return description_html

    def get_tags(self, product_input, additional_tags=None):
        return ",".join(
            [product_input["tags"]]
            + super().get_tags(product_input, additional_tags)
            + (additional_tags or [])
        )

    def get_size_field(self, product_input):
        return self.formatted_size_text_to_html_table(product_input["size_text"])

    def post_process_product_input(self, process_product_input_res, product_input):
        product_id = process_product_input_res[0]["id"]
        self.update_metafields(product_id, product_input)
        skus = [v["sku"] for v in process_product_input_res[0]["variants"]["nodes"]]
        self.update_weight(skus, product_input)
        return product_id

    def update_metafields(self, product_id, product_input):
        logger.info(f'updating metafields for {product_input["title"]}')
        size_table_html = self.get_size_field(product_input)
        if self.to_add_disclaimer_html(product_input["title"]):
            size_table_html += "<br>"
            size_table_html += "<p>注: 製造後に洗い加工を施しているため、記載されているサイズに若干の誤差が生じる場合がございます。</p>"
        self.update_size_table_html_metafield(product_id, size_table_html)
        product_care = self.text_to_simple_richtext(product_input["product_care"])
        self.update_product_care_metafield(product_id, product_care)
        self.update_filter_color(product_id, product_input)

    def to_add_disclaimer_html(self, title):
        return title.startswith("NATURAL TWILL") or title in [
            "FADE CENTER SEAM S/S TEE SHIRTS",
            "BHARAT DENIM JACKET",
        ]

    def update_weight(self, skus, product_input):
        weight = product_input.get("weight")
        if weight:
            for sku in skus:
                self.update_inventory_item_weight_by_sku(sku, weight, unit="KILOGRAMS")

    def update_filter_color(self, product_id, product_input):
        for color_option in product_input["options"]:
            filter_color = color_option["filter_color"]
            for size_option in color_option["options"]:
                sku = size_option["sku"]
                variant_id = self.variant_id_by_sku(sku)
                self.update_variant_metafield(
                    product_id, variant_id, "custom", "filter_color", filter_color
                )


def main():
    client = AlvanaClient()
    for pi in client.product_inputs_by_sheet_name("5G  LAMS WOOL CREW KNIT"):
        print(client.get_tags(pi))


if __name__ == "__main__":
    main()
