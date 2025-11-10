import logging
import re
import string
from brands.brandclientbase import BrandClientBase

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

    def get_description_html(self, product_info):
        product_care = """水や汗にさらされると、湿気によるカビや変色の恐れがあります。そのため、雨などに濡れないようご注意ください。

長時間水分に触れた場合は、革が水分を吸収する前にタオルで余分な水分を取り除いてください。内側に新聞紙などを詰め、風通しの良い場所で保管してください。"""

        return super().get_description_html(
            description=product_info["description"],
            product_care=product_care,
            material=product_info["material"],
            size_text=product_info["size_text"],
            made_in=product_info["made_in"],
            get_size_table_html_func=self.get_size_table_html,
        )

    def get_tags(self, product_info, additional_tags=None):
        tag_mapping = {
            "Standard": "Standard Line",
        }
        collection = tag_mapping.get(
            product_info["collection"], product_info["collection"]
        )
        category = tag_mapping.get(
            product_info.get("category", ""), product_info.get("category", "")
        )

        return ",".join(
            [product_info["release_date"], collection, category]
            + super().get_tags(product_info, additional_tags)
            + (additional_tags or [])
        )

    def get_size_field(self, product_info):
        size_text = product_info.get("size_text")
        if size_text:
            return self.get_size_table_html(size_text)
        else:
            logger.warning(f"no size_text for {product_info['title']}")

    def pre_process_product_info_list_to_products(self, product_info_list):
        self.merge_existing_products_as_variants()

    def process_sheet_to_products(
        self,
        sheet_name,
        additional_tags=None,
        handle_suffix=None,
        restart_at_product_name=None,
        scheduled_time=None,
    ):
        product_info_list = self.product_info_list_from_sheet(sheet_name, handle_suffix)
        if restart_at_product_name == "DO NOT CREATE":
            i = len(product_info_list)
        elif not restart_at_product_name:
            i = 0
        else:
            for i, pi in enumerate(product_info_list):
                if pi["title"] == restart_at_product_name:
                    break
        self.process_product_info_list_to_products(
            product_info_list[i:],
            additional_tags,
            scheduled_time=scheduled_time,
            handle_suffix=handle_suffix,
        )

    def process_product_info_list_to_products(
        self,
        product_info_list,
        additional_tags,
        scheduled_time=None,
        handle_suffix=None,
    ):
        for product_info in product_info_list:
            self.create_product_from_product_info(product_info, additional_tags)
            self.process_product_images(product_info, handle_suffix=handle_suffix)
        self.update_stocks(product_info_list)
        self.publish_products(product_info_list, scheduled_time=scheduled_time)


def main():
    client = ArchivepkeClient()
    for pi in client.product_info_list_from_sheet("2025.09.18(25FW Collection 2nd)"):
        print(client.get_tags(pi))


if __name__ == "__main__":
    main()
