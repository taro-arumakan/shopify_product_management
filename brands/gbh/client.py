import datetime
import logging
import pathlib
import re
import string
import textwrap
from brands.brandclientbase import BrandClientBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GbhClient(BrandClientBase):

    SHOPNAME = "gbhjapan"
    VENDOR = "GBH"
    LOCATIONS = ["Shop location"]
    PRODUCT_SHEET_START_ROW = 1

    def __init__(self, use_simple_size_format=False):
        super().__init__()
        self.use_simple_size_format = use_simple_size_format

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
        option1_attrs = {"カラー": string.ascii_lowercase.index("l")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("m"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        option2_attrs = {"サイズ": string.ascii_lowercase.index("n")}
        option2_attrs.update(
            sku=string.ascii_lowercase.index("o"),
            stock=string.ascii_lowercase.index("p"),
        )
        return option2_attrs

    @staticmethod
    def product_description_template():
        res = """
            <div id="cataldesignProduct">
                <h3>商品説明</h3>
                <p>${DESCRIPTION}</p>
                <h3>手入れ方法</h3>
                <p>${PRODUCTCARE}</p>
                <h3>サイズ・素材</h3>
                ${SIZE_TABLE}
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

        description = self.escape_html(product_input["description"])
        product_care = self.escape_html(product_input["product_care"])
        material = self.escape_html(product_input["material"])
        made_in = self.escape_html(product_input["made_in"])
        size_table_html = self.get_size_field(product_input)

        description_html = self.product_description_template()
        description_html = description_html.replace("${DESCRIPTION}", description)
        description_html = description_html.replace("${PRODUCTCARE}", product_care)
        description_html = description_html.replace("${SIZE_TABLE}", size_table_html)
        description_html = description_html.replace("${MATERIAL}", material)
        description_html = description_html.replace("${MADEIN}", made_in)

        return description_html

    def get_tags(self, product_input, additional_tags=None):
        return ",".join(
            [product_input["tags"]]
            + super().get_tags(product_input, additional_tags)
            + (additional_tags or [])
        )

    def get_size_field(self, product_input):
        if self.use_simple_size_format:
            return self.escape_html(product_input["size_text"])
        else:
            return self.formatted_size_text_to_html_table(product_input["size_text"])


class GbhClientColorOptionOnly(GbhClient):

    def product_attr_column_map(self):
        res = super().product_attr_column_map()
        res.update(product_remarks=string.ascii_lowercase.index("p"))
        return res

    def option1_attr_column_map(self):
        option1_attrs = {"カラー": string.ascii_lowercase.index("l")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("m"),
            sku=string.ascii_lowercase.index("n"),
            stock=string.ascii_lowercase.index("o"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        return {}

    def get_size_field(self, product_input):
        return product_input["size_text"]

    def add_variants_from_product_input(self, product_input):
        product_id = self.product_id_by_title(product_input["title"])
        existing_product = self.product_by_id(product_id)
        existing_variants = existing_product.get("variants", {}).get("nodes", [])

        # 既存バリアントのselectedOptionsからオプション名を取得
        existing_option_names = set()
        if existing_variants:
            for variant in existing_variants:
                for so in variant.get("selectedOptions", []):
                    existing_option_names.add(so.get("name"))

        logger.info(f"既存商品のオプション名: {sorted(existing_option_names)}")
        has_size_option = "サイズ" in existing_option_names
        logger.info(f"「サイズ」オプションの存在: {has_size_option}")

        optionss = self.segment_options_list_by_key_option(
            self.populate_option_dicts(product_input)
        )
        drive_links, skuss = self.populate_drive_ids_and_skuss(product_input)

        for drive_link, skus, options in zip(drive_links, skuss, optionss):
            logger.info(f"  processing sku: {skus} - {drive_link}")
            res = self.add_product_images(
                product_id,
                drive_link,
                f"{pathlib.Path.home()}/Downloads/gbh{datetime.date.today():%Y%m%d}/",
                f"upload_{datetime.date.today():%Y%m%d}_{skus[0]}_",
            )
            new_media_ids = [m["id"] for m in res[-1]["productCreateMedia"]["media"]]

            option_names = list(options[0]["option_values"].keys())
            variant_option_valuess = [
                list(option["option_values"].values()) for option in options
            ]
            logger.info(f"追加前のoption_names: {option_names}")
            logger.info(f"追加前のvariant_option_valuess: {variant_option_valuess}")

            if has_size_option:
                option_names.append("サイズ")
                variant_option_valuess = [
                    ov + ["FREE"] for ov in variant_option_valuess
                ]
                logger.info(f'「サイズ」="FREE"を追加しました')

            logger.info(f"追加後のoption_names: {option_names}")
            logger.info(f"追加後のvariant_option_valuess: {variant_option_valuess}")

            self.variants_add(
                product_id=product_id,
                skus=skus,
                media_ids=[],
                variant_media_ids=[new_media_ids[0]],
                option_names=option_names,
                variant_option_valuess=variant_option_valuess,
                prices=[option["price"] for option in options],
                stocks=[option["stock"] for option in options],
                location_id=self.location_id_by_name(self.LOCATIONS[0]),
            )
        self.enable_and_activate_inventory_by_product_id(
            product_id, location_names=self.LOCATIONS
        )


class GbhClientSizeOptionOnly(GbhClient):

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
        option1_attrs = {"サイズ": string.ascii_lowercase.index("n")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("m"),
            sku=string.ascii_lowercase.index("o"),
            stock=string.ascii_lowercase.index("p"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        return {}

    def get_size_field(self, product_input):
        return product_input["size_text"]

    def get_tags(self, product_input, additional_tags=None):
        return []


class GbhHomeClient(GbhClient):
    def product_attr_column_map(self):
        res = super().product_attr_column_map()
        res.pop("price")
        res.update(product_remarks=string.ascii_lowercase.index("q"))
        return res

    def option2_attr_column_map(self):
        res = super().option2_attr_column_map()
        res.update(price=string.ascii_lowercase.index("d"))
        return res


class GbhCosmeticClient(GbhClient):

    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("b"),
            tags=string.ascii_lowercase.index("c"),
            price=string.ascii_lowercase.index("e"),
            description=string.ascii_lowercase.index("g"),
            product_care=string.ascii_lowercase.index("i"),
            material=string.ascii_lowercase.index("k"),
            size_text=string.ascii_lowercase.index("l"),
            made_in=string.ascii_lowercase.index("m"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"Scent": string.ascii_lowercase.index("n")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("o"),
            sku=string.ascii_lowercase.index("p"),
            stock=string.ascii_lowercase.index("q"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        return {}

    @staticmethod
    def product_description_template():
        res = """
            <div id="cataldesignProduct">
                <h3>商品説明</h3>
                <p>${DESCRIPTION}</p>
                <h3>手入れ方法</h3>
                <p>${PRODUCTCARE}</p>
                <h3>サイズ・素材</h3>
                <table width="100%">
                  <tbody>
                    <tr>
                      <th>容量</th>
                      <td>${SIZE_TEXT}</td>
                    </tr>
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
        description = self.escape_html(product_input["description"])
        product_care = self.escape_html(product_input["product_care"])
        material = self.escape_html(product_input["material"])
        made_in = self.escape_html(product_input["made_in"])
        size_text = self.escape_html(product_input.get("size_text", ""))

        description_html = self.product_description_template()
        description_html = description_html.replace("${DESCRIPTION}", description)
        description_html = description_html.replace("${PRODUCTCARE}", product_care)
        description_html = description_html.replace("${SIZE_TEXT}", size_text)
        description_html = description_html.replace("${MATERIAL}", material)
        description_html = description_html.replace("${MADEIN}", made_in)

        return description_html

    def get_size_field(self, product_input):
        return product_input.get("size_text", "")


class GbhClientNoOptions(GbhClient):
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
            drive_link=string.ascii_lowercase.index("m"),
            sku=string.ascii_lowercase.index("n"),
            stock=string.ascii_lowercase.index("o"),
        )

    def option1_attr_column_map(self):
        return {}

    def option2_attr_column_map(self):
        return {}

    @staticmethod
    def product_description_template():
        res = """
            <div id="cataldesignProduct">
                <h3>商品説明</h3>
                <p>${DESCRIPTION}</p>
                <h3>サイズ</h3>
                ${SIZE_TABLE}
                <br/>
                <table width="100%">
                  <tbody>
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
        description = self.escape_html(product_input["description"])
        made_in = self.escape_html(product_input["made_in"])
        size_html = self.get_size_field(product_input)

        description_html = self.product_description_template()
        description_html = description_html.replace("${DESCRIPTION}", description)
        description_html = description_html.replace("${SIZE_TABLE}", size_html)
        description_html = description_html.replace("${MADEIN}", made_in)
        return description_html

    def is_title(self, line):
        return len(line.split("/")) < 2

    def box_size_text_to_html_table(self, size_line):
        parts = size_line.split("/")
        headers, rows = zip(*(map(str.strip, p.split(":")) for p in parts))
        return self.generate_table_html(headers, [rows])

    def formatted_size_text_to_html_table(self, table_text):
        try:
            return super().formatted_size_text_to_html_table(table_text)
        except RuntimeError:
            return self.box_size_text_to_html_table(table_text)

    def get_size_field(self, product_input):
        size_text = product_input["size_text"]
        lines = map(str.strip, filter(None, size_text.split("\n")))
        titles = []
        tables = []
        for line in lines:
            if self.is_title(line):
                titles.append(line)
            else:
                tables.append(self.formatted_size_text_to_html_table(line))
        return "<br />\n<br />\n".join(
            f"<h4>{title}</h4>{table}" for title, table in zip(titles, tables)
        )


def main():
    client = GbhClient()
    for pi in client.product_inputs_by_sheet_name("APPAREL 25FW 2次"):
        print(pi["title"])
        print(client.get_size_field(pi))

    client = GbhClientColorOptionOnly()
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    for pi in client.product_inputs_by_sheet_name("APPAREL 25FW 2次 (COLOR ONLY)"):
        print(pi["title"])
        print(client.get_size_field(pi))


if __name__ == "__main__":
    main()
