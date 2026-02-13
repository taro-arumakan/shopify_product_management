import json
import logging
import re
import string
import textwrap
from brands.client.brandclientbase import BrandClientBase

logger = logging.getLogger(__name__)


class SsilClient(BrandClientBase):

    SHOPNAME = "ssilkr"
    VENDOR = "ssil"
    LOCATIONS = ["SSIL Warehouse"]
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
            hs_code=string.ascii_lowercase.index("o"),
            stock=string.ascii_lowercase.index("p"),
        )
        return option2_attrs

    @staticmethod
    def product_description_template():
        res = r"""
            <div id="ssilProduct">
                <p>${DESCRIPTION}</p>
                <br>
                <p>原産国: ${MADEIN}</p>
            </div>
            """
        return textwrap.dedent(res)

    def get_description_html(self, product_input):
        description_html = self.product_description_template()
        description_html = description_html.replace(
            "${DESCRIPTION}", product_input["description"].replace("\n", "<br>")
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

    def append_ring_size_guide_link(self, size_richtext):
        additional_children_dicts = {
            "children": [
                {"type": "text", "value": ""},
                {
                    "children": [{"type": "text", "value": "Ring Size Guide"}],
                    "title": "Ring Size Guide",
                    "type": "link",
                    "url": "https://s-sil.jp/pages/ring-size-guide",
                },
                {"type": "text", "value": ""},
            ],
            "type": "paragraph",
        }
        size_richtext["children"].append(additional_children_dicts)
        return size_richtext

    def get_size_field(self, product_input):
        if size_text := product_input.get("size_text"):
            res = self.text_to_simple_richtext(size_text)
            if "ring" in list(map(str.strip, product_input["tags"].split(","))):
                res = self.append_ring_size_guide_link(res)
            return res
        else:
            logger.warning(f"no size_text for {product_input['title']}")

    def post_process_product_input(self, process_product_input_res, product_input):
        product_id = process_product_input_res[0]["id"]
        self.update_metafields(product_id, product_input)
        return product_id

    def update_metafields(self, product_id, product_input):
        logger.info(f'updating metafields for {product_input["title"]}')
        if size_text := self.get_size_field(product_input):
            self.update_product_metafield(
                product_id, "custom", "size_text", json.dumps(size_text)
            )
        if product_care := product_input.get("product_care"):
            product_care = self.text_to_simple_richtext(product_care)
            self.update_product_care_metafield(product_id, product_care)
        if material_text := product_input.get("material"):
            material_html = self.material_text_to_html(material_text)
            self.update_product_metafield(
                product_id, "custom", "material_html", material_html
            )

    def material_text_to_html(self, material_text):
        try:
            return self.formatted_material_text_to_html_table(material_text)
        except RuntimeError as e:
            return f"""<div class="material">{material_text}</div>"""

    def formatted_material_text_to_html_table(self, material_text):
        """
        [SILVER] RING: 925 SILVER / PLATING: RHODIUM
        [GOLD] RING: 925 SILVER / PLATING: 14K
        """
        heading_expression = re.compile(r"\[(.+?)\]\s*(.*)")
        header_value_expression = re.compile(r"(.+?):\s*(.+)")

        rows = []
        headers = ["Color"]

        for line in material_text.strip().split("\n"):
            match = heading_expression.match(line.strip())
            if not match:
                raise RuntimeError(f"Invalid material text format: {line}")
            row_values = [match.group(1)]
            header_value_pairs = [p.strip() for p in match.group(2).split("/")]

            for header_value_pair in header_value_pairs:
                header, value = header_value_expression.match(
                    header_value_pair.strip()
                ).groups()
                if header.strip() not in headers:
                    headers.append(header.strip())
                row_values.append(value.strip())
            rows.append(row_values)
        return super().generate_table_html(headers, rows)

    def sanity_check_product_inputs(self, product_inputs):
        for pi in product_inputs:
            try:
                self.formatted_material_text_to_html_table(pi["material"])
            except Exception as e:
                print(
                    f"failed parsing material text of {pi['title']}: {pi['material']}\n{e}"
                )
        return super().sanity_check_product_inputs(product_inputs)

    def post_process_product_inputs(self, product_inputs):
        pass


class SsilClientMaterialOptionOnly(SsilClient):
    def option1_attr_column_map(self):
        option1_attrs = {"Color": string.ascii_lowercase.index("k")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("l"),
            sku=string.ascii_lowercase.index("m"),
            hs_code=string.ascii_lowercase.index("n"),
            stock=string.ascii_lowercase.index("o"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        return {}


def main():
    client = SsilClient()
    for pi in client.product_inputs_by_sheet_name(
        "material & size options (rings etc)"
    ):
        print(client.get_tags(pi))


if __name__ == "__main__":
    main()
