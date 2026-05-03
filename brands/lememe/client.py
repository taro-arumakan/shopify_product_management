import logging
import string
import textwrap
from brands.client.brandclientbase import BrandClientBase

logger = logging.getLogger(__name__)


class LememeClient(BrandClientBase):

    SHOPNAME = "lememek"
    VENDOR = "lememe"
    LOCATIONS = ["Shop location"]

    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("c"),
            tags=string.ascii_lowercase.index("d"),
            price=string.ascii_lowercase.index("f"),
            description=string.ascii_lowercase.index("h"),
            product_care_option=string.ascii_lowercase.index("i"),
            material=string.ascii_lowercase.index("j"),
            size_text=string.ascii_lowercase.index("k"),
            made_in=string.ascii_lowercase.index("m"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"Color": string.ascii_lowercase.index("n")}
        option1_attrs.update(
            filter_color=string.ascii_lowercase.index("n"),
            drive_link=string.ascii_lowercase.index("p"),
            sku=string.ascii_lowercase.index("o"),
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

    def get_size_field(self, product_input):
        if size_text := product_input.get("size_text"):
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
            logger.warning(f"no size_text for {product_input['title']}")

    def post_process_product_input(self, process_product_input_res, product_input):
        product_id = process_product_input_res["create_product"]["id"]
        self.update_metafields(product_id, product_input)
        return product_id

    def update_metafields(self, product_id, product_input):
        logger.info(f'updating metafields for {product_input["title"]}')
        size_table_html = self.get_size_field(product_input)
        self.update_size_table_html_metafield(product_id, size_table_html)
        self.update_badges_metafield(product_id, ["NEW"])
        product_care_page_title = (
            "Product Care - " + product_input.get("product_care_option", "").strip()
        )
        self.update_product_care_page_metafield(product_id, product_care_page_title)
        for option in product_input["options"]:
            if filter_color := option.get("filter_color"):
                sku = option["sku"]
                variant = self.variant_by_sku(sku)
                variant_id = variant["id"]
                self.update_variant_metafield(
                    product_id, variant_id, "custom", "filter_color", filter_color
                )


class LememeClientApparel(LememeClient):

    def option1_attr_column_map(self):
        option1_attrs = {"Color": string.ascii_lowercase.index("n")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("s"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        option2_attrs = {"sku": string.ascii_lowercase.index("p")}
        option2_attrs.update(
            Size=string.ascii_lowercase.index("o"),
            stock=string.ascii_lowercase.index("q"),
        )
        return option2_attrs


def main():
    client = LememeClientApparel(product_sheet_start_row=1)
    titles = [
        "Aude Classic Jacket Butter",
        "Aude Classic Jacket CharcoalGrey",
        "Mouchou High Neck Leather Jumper Ivory",
        "Mouchou High Neck Leather Jumper Black",
        "Fitte Slim Bootcut Slacks Black",
        "Sole One-Tuck Wide Pants Black",
        "Sole One-Tuck Wide Pants White",
    ]
    client.sanity_check_sheet(
        sheet_name="0305_RTW_spring",
        product_inputs_filter_func=lambda pi: pi["title"] in titles,
    )


if __name__ == "__main__":
    main()
