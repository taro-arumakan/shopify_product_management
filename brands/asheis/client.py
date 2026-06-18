import logging
import re
import string
import textwrap
from brands.client.brandclientbase import BrandClientBase


logger = logging.getLogger(__name__)


class AsheisClient(BrandClientBase):

    SHOPNAME = "asheis"
    VENDOR = "asheis"
    LOCATIONS = [
        "Shop location"
    ]  # TODO: verify; the current token lacks read_locations
    BRAND_NAME = "ASHEIS"

    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("a"),
            tags=string.ascii_lowercase.index("b"),
            price=string.ascii_lowercase.index("c"),
            description=string.ascii_lowercase.index("d"),
            product_care=string.ascii_lowercase.index("e"),
            material=string.ascii_lowercase.index("f"),
            size_text=string.ascii_lowercase.index("g"),
            made_in=string.ascii_lowercase.index("i"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"カラー": string.ascii_lowercase.index("j")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("l"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        option2_attrs = {"サイズ": string.ascii_lowercase.index("m")}
        option2_attrs.update(
            sku=string.ascii_lowercase.index("q"),
            stock=string.ascii_lowercase.index("o"),
        )
        return option2_attrs

    @staticmethod
    def product_description_template():
        res = r"""
            <div id="asheisProduct">
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
        # for key in ["description", "material", "made_in"]:
        #     assert product_input.get(key), f'no {key} for {product_input["title"]}'

        # description cells in the sheet are wrapped in literal double quotes
        description = product_input["description"].strip().strip('"“”').strip()
        description_html = self.product_description_template()
        description_html = description_html.replace(
            "${DESCRIPTION}", description.replace("\n", "<br>")
        )
        description_html = description_html.replace(
            "${MATERIAL}", product_input.get("material", "").replace("\n", "<br>")
        )
        description_html = description_html.replace(
            "${MADEIN}", product_input["made_in"]
        )
        return description_html

    # asheis 寸法 is its own shape, e.g.
    #   [0] 着丈116 / 身幅73 / 袖幅(二の腕)45.5
    #   裏地：背裏
    #   [1] 着丈122 / 身幅73 / 袖幅(二の腕)45.5
    #   裏地：背裏
    # Quirks vs. the shared formatted_size_text_to_html_table: the [size] prefix is
    # dropped on single-size items, each size may be followed by a 裏地：xxx line, and
    # values carry annotations like 97(ﾀｯｸなし). Parse it here rather than loosening the
    # shared helper, which gbh/lememe/blossom/alvana also rely on.
    size_prefix_expression = re.compile(r"^\[(.+?)\]\s*(.*)$")
    lining_expression = re.compile(r"^裏地\s*[:：]\s*(.+)$")
    placeholder_expression = re.compile(r"[○◯〇]+")
    # label = leading non-numeric text, value = from the first digit onward (keeps any
    # trailing annotation and ranges like 72.5〜82.5); label-only tokens get an empty value.
    measure_expression = re.compile(r"^(.*?)([0-9０-９].*)$")
    # set items pack two measurements in one segment, split by a space before the next
    # section label, e.g. "ゆき80 (インナー)着丈57" -> "ゆき80" / "(インナー)着丈57".
    section_break_expression = re.compile(r"(?<=[0-9０-９])\s+(?=[(（])")

    def sole_size(self, product_input):
        sizes = {
            o2["サイズ"]
            for o1 in product_input.get("options", [])
            for o2 in o1.get("options", [])
        }
        if len(sizes) == 1:
            return re.sub(r"\s*\(.*?\)\s*$", "", sizes.pop()).strip()
        return ""

    def parse_measurements(self, text):
        pairs = []
        text = self.section_break_expression.sub(" / ", text)
        for token in text.split("/"):
            token = self.placeholder_expression.sub("", token).strip()
            if not token:
                continue
            if m := self.measure_expression.match(token):
                pairs.append((m.group(1).strip(), m.group(2).strip()))
            else:
                pairs.append((token, ""))
        return pairs

    def parse_size_rows(self, size_text, default_size=""):
        size_text = (
            size_text.replace("／", "/").replace("\r\n", "\n").replace("\r", "\n")
        )
        rows = []  # [[size, [(label, value), ...]], ...]
        for line in size_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            if m := self.size_prefix_expression.match(line):
                rows.append([m.group(1).strip(), self.parse_measurements(m.group(2))])
            elif m := self.lining_expression.match(line):
                if not rows:
                    rows.append([default_size, []])
                rows[-1][1].append(("裏地", m.group(1).strip()))
            else:
                pairs = self.parse_measurements(line)
                if rows:
                    rows[-1][1].extend(pairs)
                else:
                    rows.append([default_size, pairs])
        return rows

    def get_size_field(self, product_input):
        size_text = product_input.get("size_text")
        if not size_text:
            return ""
        rows = self.parse_size_rows(size_text, self.sole_size(product_input))
        headers = ["Size"]
        for _, pairs in rows:
            for label, _ in pairs:
                if label not in headers:
                    headers.append(label)
        table_rows = [
            [size] + [dict(pairs).get(h, "") for h in headers[1:]]
            for size, pairs in rows
        ]
        return self.generate_table_html(headers, table_rows)

    def post_process_product_input(self, process_product_input_res, product_input):
        product_id = process_product_input_res["create_product"]["id"]
        self.update_metafields(product_id, product_input)

    def update_metafields(self, product_id, product_input):
        logger.info(f'updating metafields for {product_input["title"]}')
        self.update_size_table_html_metafield(
            product_id, self.get_size_field(product_input)
        )
        # product_care = product_input.get("product_care")
        # self.update_product_care_metafield(
        #     product_id, self.text_to_simple_richtext(product_care)
        # )


def update_metafields():
    logging.basicConfig(level=logging.DEBUG)
    client = AsheisClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag="opening",
    )
    product_inputs = client.product_inputs_by_sheet_name("Products Master")
    for pi in product_inputs:
        p = client.product_by_title(pi["title"])
        client.update_metafields(p["id"], pi)


def main():
    logging.basicConfig(level=logging.DEBUG)
    client = AsheisClient(
        product_sheet_start_row=1,
        remove_existing_new_product_indicators=False,
        products_season_tag="opening",
    )
    client.process_sheet_to_products(
        "Products Master"
        # , restart_at_product_title="HIGH-NECK LACE TOP"
    )


if __name__ == "__main__":
    update_metafields()
