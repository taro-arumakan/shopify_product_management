import logging
import re
import string
from brands.client.brandclientbase import BrandClientBase

logger = logging.getLogger(__name__)


class ArchivepkeClient(BrandClientBase):

    SHOPNAME = "archive-epke"
    VENDOR = "archive-epke"
    LOCATIONS = ["Archivépke Warehouse", "Envycube Warehouse"]
    PRODUCT_SHEET_START_ROW = 3

    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("d"),
            release_date=string.ascii_lowercase.index("c"),
            collection=string.ascii_lowercase.index("f"),
            category=string.ascii_lowercase.index("h"),
            description=string.ascii_lowercase.index("q"),
            size_text=string.ascii_lowercase.index("t"),
            material=string.ascii_lowercase.index("u"),
            made_in=string.ascii_lowercase.index("v"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"カラー": string.ascii_lowercase.index("i")}
        option1_attrs.update(
            sku=string.ascii_lowercase.index("e"),
            price=string.ascii_lowercase.index("l"),
            drive_link=string.ascii_lowercase.index("o"),
            stock=string.ascii_lowercase.index("m"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        return {}

    def get_size_table_html(self, size_text):
        """Convert size text to HTML table for archivepke format"""
        kv_pairs = list(map(str.strip, re.split("[\n/]", size_text)))
        headers, values = zip(*[kv_pair.split(" ") for kv_pair in kv_pairs])
        return self.generate_table_html(headers, [values])

    def get_description_html(self, product_input):
        product_care = """水や汗にさらされると、湿気によるカビや変色の恐れがあります。そのため、雨などに濡れないようご注意ください。

長時間水分に触れた場合は、革が水分を吸収する前にタオルで余分な水分を取り除いてください。内側に新聞紙などを詰め、風通しの良い場所で保管してください。"""

        return super().get_description_html(
            description=product_input["description"],
            product_care=product_care,
            material=product_input["material"],
            size_html=self.get_size_field(product_input),
            made_in=product_input["made_in"],
        )

    def get_tags(self, product_input, additional_tags=None):
        tag_mapping = {
            "Standard": "Standard Line",
        }
        collection = tag_mapping.get(
            product_input["collection"], product_input["collection"]
        )
        category = tag_mapping.get(
            product_input.get("category", ""), product_input.get("category", "")
        )

        return ",".join(
            [product_input["release_date"], collection, category]
            + super().get_tags(product_input, additional_tags)
            + (additional_tags or [])
        )

    def get_size_field(self, product_input):
        size_text = product_input.get("size_text")
        if size_text:
            return self.get_size_table_html(size_text)
        else:
            logger.warning(f"no size_text for {product_input['title']}")

    def pre_process_product_inputs(self, product_inputs):
        self.merge_existing_products_as_variants()
        super().pre_process_product_inputs(product_inputs=product_inputs)


def main():
    client = ArchivepkeClient()
    for pi in client.product_inputs_by_sheet_name("2025.09.18(25FW Collection 2nd)"):
        print(client.get_tags(pi))


if __name__ == "__main__":
    main()
