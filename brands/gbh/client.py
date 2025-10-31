import copy
import logging
import string
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
            title=string.ascii_lowercase.index("f"),
            collection=string.ascii_lowercase.index("c"),
            category=string.ascii_lowercase.index("d"),
            category2=string.ascii_lowercase.index("e"),
            release_date=string.ascii_lowercase.index("b"),
            description=string.ascii_lowercase.index("q"),
            product_care=string.ascii_lowercase.index("s"),
            material=string.ascii_lowercase.index("u"),
            made_in=string.ascii_lowercase.index("v"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"カラー": string.ascii_lowercase.index("g")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("o"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        option2_attrs = {"サイズ": string.ascii_lowercase.index("h")}
        option2_attrs.update(
            price=string.ascii_lowercase.index("l"),
            sku=string.ascii_lowercase.index("i"),
            stock=string.ascii_lowercase.index("m"),
            size_text=string.ascii_lowercase.index("t"),
        )
        return option2_attrs

    def merge_size_texts(self, product_info):
        if product_info["title"] in ["WRAP SKIRT & PANTS"]:
            size_text = product_info["options"][0]["options"][0]["size_text"]
        else:
            # uniquify size and size texts, keeping the order
            sizes, size_texts = map(
                dict.fromkeys,
                zip(
                    *[
                        (o2["サイズ"], o2["size_text"])
                        for o1 in product_info["options"]
                        for o2 in o1["options"]
                    ]
                ),
            )
            size_text = "\n".join(
                f"[{size}] {st}" for size, st in zip(sizes, size_texts)
            )
        return size_text

    def get_description_html(self, product_info):
        return super().get_description_html(
            description=product_info["description"],
            product_care=product_info["product_care"],
            material=product_info["material"],
            size_text=product_info["size_text"],
            made_in=product_info["made_in"],
        )

    def get_tags(self, product_info, additional_tags=None):
        return ",".join(
            [
                product_info["category"],
                product_info["category2"],
                product_info["release_date"],
            ]
            + (additional_tags or [])
        )

    def get_size_field(self, product_info):
        size_text = self.merge_size_texts(product_info)
        return super().formatted_size_text_to_html_table(size_text)


def main():
    client = GbhClient()
    client.sanity_check_sheet("APPAREL 25FW (WINTER 1次)")


if __name__ == "__main__":
    main()
