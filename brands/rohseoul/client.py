import logging
import string
from brands.client.brandclientbase import BrandClientBase
import textwrap


logger = logging.getLogger(__name__)

# Fixed (no per-product variables), used both in the description template below
# and by adhoc/add_after_service_section.py to backfill existing products.
AFTER_SERVICE_HTML = textwrap.dedent(
    """
    <h3>アフターサービス</h3>
    <p>ローソウルの保証期間は6ヶ月です。製品購入後6ヶ月以内に発生した製品の不具合は無償で修理対応いたします。詳しくは<a href="https://rohseoul.jp/pages/warranty-certificate-and-after-service">こちら</a></p>
    """
).strip()


class RohseoulClient(BrandClientBase):

    SHOPNAME = "rohseoul"
    VENDOR = "rohseoul"
    LOCATIONS = ["Shop location"]
    BRAND_NAME = "ROH SEOUL"

    @staticmethod
    def product_description_template():
        res = """
            <div id="cataldesignProduct">
                <h3>商品説明</h3>
                <p>${DESCRIPTION}</p>
                <h3>手入れ方法</h3>
                <p>${PRODUCTCARE}</p>
                ${AFTER_SERVICE}
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
        return textwrap.dedent(res).replace("${AFTER_SERVICE}", AFTER_SERVICE_HTML)

    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("e"),
            release_date=string.ascii_lowercase.index("c"),
            collection=string.ascii_lowercase.index("g"),
            bag_category=string.ascii_lowercase.index("h"),
            category=string.ascii_lowercase.index("i"),
            description=string.ascii_lowercase.index("s"),
            size_text=string.ascii_lowercase.index("v"),
            material=string.ascii_lowercase.index("w"),
            made_in=string.ascii_lowercase.index("x"),
        )

    def option1_attr_column_map(self):
        column_variant_attrs = {"カラー": string.ascii_lowercase.index("j")}
        column_variant_attrs.update(
            sku=string.ascii_lowercase.index("f"),
            price=string.ascii_lowercase.index("m"),
            stock=string.ascii_lowercase.index("n"),
            drive_link=string.ascii_lowercase.index("p"),
            status=string.ascii_lowercase.index("a"),
        )
        return column_variant_attrs

    def option2_attr_column_map(self):
        return {}

    def get_description_html(self, product_input):
        product_care = textwrap.dedent(
            """
            革表面に跡や汚れなどが残る場合がありますが、天然皮革の特徴である不良ではございませんのでご了承ください。また、時間経過により金属の装飾や革の色が変化する場合がございますが、製品の欠陥ではありません。あらかじめご了承ください。
            1: 熱や直射日光に長時間さらされると革に変色が生じることがありますのでご注意ください。
            2: 変形の恐れがありますので、無理のない内容量でご使用ください。
            3: 水に弱い素材です。濡れた場合は柔らかい布で水気を除去した後、乾燥させてください。
            4: 使用しないときはダストバッグに入れ、涼しく風通しのいい場所で保管してください。
            5: アルコール、オイル、香水、化粧品などにより製品が損傷することがありますので、ご使用の際はご注意ください。
            """
        ).strip()
        return self.format_description_html(
            product_input["description"],
            product_care,
            product_input["material"],
            size_html=self.get_size_field(product_input),
            made_in=product_input["made_in"],
        )

    def get_tags_from_product_input(self, product_input):
        return [
            product_input["release_date"],
            product_input["collection"],
            product_input["category"],
            product_input["bag_category"],
        ]

    @staticmethod
    def get_size_table_html(size_text):
        lines = list(filter(None, map(str.strip, size_text.split("\n"))))
        kv_pairs = [line.rsplit(" ", 1) for line in lines]
        kv_pairs = [
            pair if len(pair) == 2 else ["Weight", pair[0]] for pair in kv_pairs
        ]
        headers, values = zip(*kv_pairs)
        res = "<table><thead><tr>"
        for header in headers:
            res += f"<th>{header.replace(')', '')}</th>"
        res += "</tr></thead><tbody><tr>"
        for value in values:
            res += f"<td>{value}</td>"
        res += "</tr></tbody></table>"
        return res

    def get_size_field(self, product_input):
        return self.get_size_table_html(product_input["size_text"])

    def pre_process_product_inputs(self, product_inputs):
        self.merge_existing_products_as_variants_by_title()
        super().pre_process_product_inputs(product_inputs=product_inputs)


def main():
    client = RohseoulClient()
    for pi in client.product_inputs_by_sheet_name("25FW 2ST 민하가방"):
        print(client.get_tags(pi))


if __name__ == "__main__":
    main()
