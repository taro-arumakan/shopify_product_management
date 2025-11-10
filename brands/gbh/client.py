import logging
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
            <!DOCTYPE html>
            <html>
            <body>
            <div id="cataldesignProduct">
                <div class="shipping">
                <p><span style="color: #ff2a00;"><strong>商品の到着は、支払い完了後10営業日以内が目安となります。</strong></span><br></p>
                <p>※生産上の都合によりお届け予定日が前後する場合もございます。発送時期はあくまでも目安としてご確認ください。</p>
                <p>※商品のご用意ができない場合を除き、ご注文のキャンセルは一切お受けできません。</p>
                <p>※合わせ買いの場合、すべての商品のご用意が出来次第発送とさせて頂きます。予めご了承お願い致します。</p>
                <p>※こちらの商品は指定日配送を承ることが出来かねます。</p>
                </div>
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
                <h3>その他注意事項</h3>
                <ul>
                <li>お使いのPC・携帯等端末の環境により、実際の製品と画像の色味が若干異なる場合がございます。予めご了承ください。</li>
                <li>独自の計測法で採寸しております。多少の誤差はご了承下さい。</li>
                <li>注文が殺到した場合、決済システムの都合上、在庫切れ後に決済確定され、ご注文をキャンセルさせていただくことがございます。キャンセルする場合はメールにてご連絡致します。予めご了承ください。</li>
                <li>住所不定と長期不在などによって返送された場合はキャンセル扱いとなります。</li>
                <li>配送に関する注意事項をご確認下さい。</li>
                </ul>
            </div>
            </body>

            </html>
        """
        return textwrap.dedent(res)

    def get_description_html(self, product_info):

        description = self.escape_html(product_info["description"])
        product_care = self.escape_html(product_info["product_care"])
        material = self.escape_html(product_info["material"])
        made_in = self.escape_html(product_info["made_in"])
        size_table_html = self.get_size_field(product_info)

        description_html = self.product_description_template()
        description_html = description_html.replace("${DESCRIPTION}", description)
        description_html = description_html.replace("${PRODUCTCARE}", product_care)
        description_html = description_html.replace("${SIZE_TABLE}", size_table_html)
        description_html = description_html.replace("${MATERIAL}", material)
        description_html = description_html.replace("${MADEIN}", made_in)

        return description_html

    def get_tags(self, product_info, additional_tags=None):
        return ",".join(
            [product_info["tags"]]
            + super().get_tags(product_info, additional_tags)
            + (additional_tags or [])
        )

    @staticmethod
    def formatted_size_text_to_html_table(size_text):
        """
        [FREE]  LENGTH 69.7 / SHOULDER RAGLAN / CHEST 69.8 / SLEEVE 83.5 / HEM 64

        [S] : LENGTH 104 / WAIST 37 / HIP 52 / HEM 28 / FRONT RISE 26
        [M] : LENGTH 105 / WAIST 39 / HIP 54 / HEM 29 / FRONT RISE 27
        """
        size_expression = re.compile(r"\[(.+?)\][\s\:]+(.*)")
        header_value_expression = re.compile(r"([^\d]+)\s*([\d\.]+)")

        rows = []
        headers = ["Size"]

        for line in size_text.strip().split("\n"):
            match = size_expression.match(line.strip())
            if not match:
                raise RuntimeError(f"Invalid size text format: {line}")
            row_values = [match.group(1)]
            header_value_pairs = [p.strip() for p in match.group(2).split("/")]

            for header_value_pair in header_value_pairs:
                header, value = header_value_pair.rsplit(" ", 1)
                if header.strip() not in headers:
                    headers.append(header.strip())
                row_values.append(value.strip())
            rows.append(row_values)
        return BrandClientBase.generate_table_html(headers, rows)

    def get_size_field(self, product_info):
        return self.formatted_size_text_to_html_table(product_info["size_text"])


class GbhClientColorOptionOnly(GbhClient):

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


def main():
    client = GbhClient()
    for pi in client.product_info_list_from_sheet("APPAREL 25FW 2次"):
        print(pi["title"])
        print(client.get_size_field(pi))

    client = GbhClientColorOptionOnly()
    client.REMOVE_EXISTING_NEW_PRODUCT_INDICATORS = False
    for pi in client.product_info_list_from_sheet("APPAREL 25FW 2次 (COLOR ONLY)"):
        print(pi["title"])
        print(client.get_size_field(pi))


if __name__ == "__main__":
    main()
