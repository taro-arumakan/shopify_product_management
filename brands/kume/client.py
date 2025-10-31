import logging
import string
from brands.brandclientbase import BrandClientBase

logger = logging.getLogger(__name__)


class KumeClient(BrandClientBase):

    SHOPNAME = "kumej"
    VENDOR = "KUME"
    LOCATIONS = ["KUME Warehouse", "Envycube Warehouse"]
    PRODUCT_SHEET_START_ROW = 2

    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("d"),
            release_date=string.ascii_lowercase.index("c"),
            category=string.ascii_lowercase.index("e"),
            collection=string.ascii_lowercase.index("f"),
            description=string.ascii_lowercase.index("h"),
            product_care=string.ascii_lowercase.index("j"),
            material=string.ascii_lowercase.index("k"),
            size_text=string.ascii_lowercase.index("l"),
            made_in=string.ascii_lowercase.index("m"),
            price=string.ascii_lowercase.index("p"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"カラー": string.ascii_lowercase.index("q")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("r"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        option2_attrs = {"サイズ": string.ascii_lowercase.index("s")}
        option2_attrs.update(
            sku=string.ascii_lowercase.index("t"),
            stock=string.ascii_lowercase.index("u"),
        )
        return option2_attrs

    def parse_line_to_header_and_values(self, line: str):
        size, rest = line.split("]", 1)
        size = size.replace("[", "").strip()
        kv_pairs = list(map(str.strip, rest.strip().split("/")))
        headers = [""] + [pair.split(" ")[0] for pair in kv_pairs]
        values = [size] + [pair.split(" ", 1)[1].strip() for pair in kv_pairs]
        return headers, values

    def parse_table_text_to_html(self, table_text: str):
        lines = filter(None, table_text.split("\n"))
        valuess = []
        for line in lines:
            headers, values = self.parse_line_to_header_and_values(line)
            valuess.append(values)
        return self.generate_table_html(headers, valuess)

    def heading_headers_values_to_html(self, heading, headers, valuess):
        res = self.generate_table_html(headers, valuess)
        res = f"<h3>{heading}</h3>{res}"
        return res

    def parse_headings_and_table_text_to_html(self, size_text: str):
        lines = filter(None, size_text.split("\n"))
        headings, headerss, valuesss = [], [], []
        for line in lines:
            size_or_heading, rest = line.split("]", 1)
            rest = rest.strip()
            if not rest:
                headings.append(size_or_heading.replace("[", "").strip())
            else:
                headers, values = self.parse_line_to_header_and_values(line)
                if len(headings) > len(headerss):
                    headerss.append(headers)
                    valuesss.append([])
                valuesss[-1].append(values)
        return "\n<br><br>\n\n".join(
            [
                self.heading_headers_values_to_html(heading, headers, valuess)
                for heading, headers, valuess in zip(headings, headerss, valuesss)
            ]
        )

    def parse_size_text_to_html(self, size_text):
        lines = filter(None, size_text.split("\n"))
        with_headings = False
        for line in lines:
            _, rest = line.split("]", 1)
            rest = rest.strip()
            if not rest:
                with_headings = True
                break
        if not with_headings:
            return self.parse_table_text_to_html(size_text)
        else:
            return self.parse_headings_and_table_text_to_html(size_text)

    def get_description_html(self, product_info):
        return super().get_description_html(
            description=product_info["description"],
            product_care=product_info["product_care"],
            material=product_info["material"],
            size_text=product_info["size_text"],
            made_in=product_info["made_in"],
            get_size_table_html_func=self.parse_size_text_to_html,
        )

    def get_tags(self, product_info, additional_tags=None):
        category_tags = list(map(str.strip, product_info["category"].split(" AND ")))
        return ",".join(
            category_tags + [product_info["collection"]] + (additional_tags or [])
        )

    def get_size_field(self, product_info):
        size_text = product_info.get("size_text")
        if size_text:
            return self.parse_size_text_to_html(size_text)
        else:
            logger.warning(f"no size_text for {product_info['title']}")


def main():
    client = KumeClient()
    client.sanity_check_sheet("25FW")


if __name__ == "__main__":
    main()
