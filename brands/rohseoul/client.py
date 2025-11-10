import logging
import string
from brands.brandclientbase import BrandClientBase
import textwrap


logger = logging.getLogger(__name__)


class RohseoulClient(BrandClientBase):

    SHOPNAME = "rohseoul"
    VENDOR = "rohseoul"
    LOCATIONS = ["Shop location"]
    PRODUCT_SHEET_START_ROW = 2

    def sanity_check_product_info_list(self, product_info_list):
        return super().sanity_check_product_info_list(
            product_info_list, text_to_html_func=self.get_size_table_html
        )

    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("e"),
            release_date=string.ascii_lowercase.index("c"),
            collection=string.ascii_lowercase.index("g"),
            bag_category=string.ascii_lowercase.index("h"),
            category=string.ascii_lowercase.index("i"),
            description=string.ascii_lowercase.index("r"),
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

    def get_description_html(self, product_info):
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
        return super().get_description_html(
            product_info["description"],
            product_care,
            product_info["material"],
            product_info["size_text"],
            product_info["made_in"],
        )

    def get_tags(self, product_info, additional_tags=None):
        return ",".join(
            [
                product_info["release_date"],
                product_info["collection"],
                product_info["category"],
                product_info["bag_category"],
            ]
            + super().get_tags(product_info, additional_tags)
            + (additional_tags or [])
        )

    def get_size_field(self, product_info):
        size_text = product_info["size_text"]
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

    def pre_process_product_info_list_to_products(self, product_info_list):
        self.merge_existing_products_as_variants()


def main():
    client = RohseoulClient()
    for pi in client.product_info_list_from_sheet("25FW 2ST 민하가방"):
        print(client.get_tags(pi))


if __name__ == "__main__":
    main()
