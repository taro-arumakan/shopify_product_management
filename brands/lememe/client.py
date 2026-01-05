import logging
import string
import textwrap
from brands.brandclientbase import BrandClientBase

logger = logging.getLogger(__name__)


class LememeClient(BrandClientBase):

    SHOPNAME = "lememek"
    VENDOR = "lememe"
    LOCATIONS = ["Shop location"]
    PRODUCT_SHEET_START_ROW = 1

    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("b"),
            tags=string.ascii_lowercase.index("c"),
            price=string.ascii_lowercase.index("e"),
            description=string.ascii_lowercase.index("g"),
            product_care_option=string.ascii_lowercase.index("h"),
            material=string.ascii_lowercase.index("j"),
            size_text=string.ascii_lowercase.index("k"),
            made_in=string.ascii_lowercase.index("l"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"Color": string.ascii_lowercase.index("m")}
        option1_attrs.update(
            filter_color=string.ascii_lowercase.index("n"),
            drive_link=string.ascii_lowercase.index("o"),
            sku=string.ascii_lowercase.index("p"),
            stock=string.ascii_lowercase.index("q"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        return {}

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

    def get_tags(self, product_info, additional_tags=None):
        return ",".join(
            [product_info["tags"]]
            + super().get_tags(product_info, additional_tags)
            + (additional_tags or [])
        )

    def get_size_field(self, product_info):
        if size_text := product_info.get("size_text"):
            lines = list(filter(None, map(str.strip, size_text.split("/"))))
            kv_pairs = [line.rsplit(" ", 1) for line in lines]
            headers, values = zip(*kv_pairs)
            res = "<table><thead><tr>"
            for header in headers:
                res += f"<th>{header.replace(')', '')}</th>"
            res += "</tr></thead><tbody><tr>"
            for value in values:
                res += f"<td>{value}</td>"
            res += "</tr></tbody></table>"
            return res
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
        size_table_html = self.get_size_field(product_info)
        self.update_size_table_html_metafield(product_id, size_table_html)
        product_care_page_title = (
            "Product Care - " + product_info.get("product_care_option", "").strip()
        )
        self.update_badges_metafield(product_id, ["NEW"])
        self.update_product_care_page_metafield(product_id, product_care_page_title)
        for option in product_info["options"]:
            sku = option["sku"]
            filter_color = option["filter_color"]
            variant = self.variant_by_sku(sku)
            variant_id = variant["id"]
            self.update_variant_metafield(
                product_id, variant_id, "custom", "filter_color", filter_color
            )

    def remove_existing_new_badges(self):
        self._remove_existing_new_badges()


def main():
    client = LememeClient()
    for pi in client.product_info_list_from_sheet("1114_Small Goods"):
        print(client.get_tags(pi))


if __name__ == "__main__":
    main()
