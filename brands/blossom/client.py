import logging
import string
import textwrap
from brands.client.brandclientbase import BrandClientBase

logger = logging.getLogger(__name__)


class BlossomClient(BrandClientBase):

    SHOPNAME = "blossomhcompany"
    VENDOR = "blossom"
    LOCATIONS = ["Blossom Warehouse"]
    PRODUCT_SHEET_START_ROW = 1

    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("a"),
            tags=string.ascii_lowercase.index("b"),
            series_name=string.ascii_lowercase.index("c"),
            price=string.ascii_lowercase.index("e"),
            description=string.ascii_lowercase.index("g"),
            product_care=string.ascii_lowercase.index("h"),
            material=string.ascii_lowercase.index("i"),
            size_text=string.ascii_lowercase.index("j"),
            made_in=string.ascii_lowercase.index("k"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"Color": string.ascii_lowercase.index("l")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("m"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        option2_attrs = {"Size": string.ascii_lowercase.index("n")}
        option2_attrs.update(
            sku=string.ascii_lowercase.index("o"),
            stock=string.ascii_lowercase.index("p"),
        )
        return option2_attrs

    @staticmethod
    def product_description_template():
        res = r"""
            <div id="cataldesignProduct">
                <p>${DESCRIPTION}</p>
                <br>
                <table width="100%">
                <tbody>
                    <tr>
                    <td>素材</td>
                    <td>${MATERIAL}</td>
                    </tr>
                    <tr>
                    <td>原産国</td>
                    <td>${MADEIN}</td>
                    </tr>
                </tbody>
                </table>
            </div>
            """
        return textwrap.dedent(res)

    def get_description_html(self, product_input):
        description_html = self.product_description_template()
        description_html = description_html.replace(
            "${DESCRIPTION}", product_input["description"].replace("\n", "<br>")
        )
        description_html = description_html.replace(
            "${MATERIAL}", product_input["material"]
        )
        description_html = description_html.replace(
            "${MADEIN}", product_input.get("made_in", "KOREA")
        )
        return description_html

    def get_tags(self, product_input, additional_tags=None):
        return ",".join(
            [product_input["tags"]]
            + super().get_tags(product_input, additional_tags)
            + (additional_tags or [])
        )

    def get_size_field(self, product_input):
        if size_text := product_input.get("size_text"):
            return self.formatted_size_text_to_html_table(size_text)
        else:
            logger.warning(f"no size_text for {product_input['title']}")

    def post_process_product_input(self, process_product_input_res, product_input):
        product_id = process_product_input_res["create_product"]["id"]
        self.update_metafields(product_id, product_input)
        return product_id

    def update_metafields(self, product_id, product_input):
        logger.info(f'updating metafields for {product_input["title"]}')
        if size_table_html := self.get_size_field(product_input):
            self.update_product_metafield(
                product_id, "custom", "size_table_html", size_table_html
            )
        self.update_badges_metafield(product_id, ["NEW"])
        if product_care := product_input.get("product_care", "").strip():
            self.update_product_care_metafield(
                product_id, self.text_to_simple_richtext(product_care)
            )
        if series_name := product_input.get("series_name", "").strip():
            self.update_product_metafield(
                product_id,
                "custom",
                "series_name",
                series_name,
            )

    def post_process_product_inputs(self, product_inputs):
        series_names = set(
            p["series_name"] for p in product_inputs if p.get("series_name")
        )
        for series_name in series_names:
            self.create_series_collection(series_name)
        super().post_process_product_inputs(product_inputs)

    def create_series_collection(self, series_name):
        try:
            self.collection_by_title(series_name)
            logger.info(f"Collection for series '{series_name}' already exists.")
        except RuntimeError as e:
            if str(e).startswith("No collections found for "):
                logger.info(
                    f'Creating and publishing collection for series "{series_name}"'
                )
                self.collection_create_by_metafield_value(
                    collection_title=series_name,
                    namespace="custom",
                    key="series_name",
                    value=series_name,
                )
            else:
                raise e

    def process_series_products(self, series_name, products):
        self.create_series_collection(series_name)
        for product in products:
            logger.info(f"Assigning series name {series_name} to {product['title']}")
            self.update_product_metafield(
                product_id=product["id"],
                metafield_namespace="custom",
                metafield_key="series_name",
                value=series_name,
            )


class BlossomClientClothes(BlossomClient):
    pass


class BlossomClientShoes(BlossomClient):
    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("b"),
            series=string.ascii_lowercase.index("c"),
            tags=string.ascii_lowercase.index("d"),
            price=string.ascii_lowercase.index("f"),
            description=string.ascii_lowercase.index("h"),
            product_care=string.ascii_lowercase.index("j"),
            material=string.ascii_lowercase.index("l"),
            size_text=string.ascii_lowercase.index("m"),
            made_in=string.ascii_lowercase.index("n"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"Color": string.ascii_lowercase.index("o")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("p"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        option2_attrs = {"Size": string.ascii_lowercase.index("q")}
        option2_attrs.update(
            sku=string.ascii_lowercase.index("r"),
            stock=string.ascii_lowercase.index("s"),
        )
        return option2_attrs

    def get_size_field(self, product_input):
        """
        FRONT HEEL 0.3 / BACK HEEL 7
        """
        size_text = product_input["size_text"].strip()
        assert (
            len(size_text.strip().split("\n")) == 1
        ), f"expecting single line size text: {size_text}"
        header_value_pairs = [p.strip() for p in size_text.split(" / ")]
        headers, values = zip(*(p.rsplit(" ", 1) for p in header_value_pairs))
        return BlossomClientShoes.generate_table_html(headers, [values])

    def post_process_product_input(self, process_product_input_res, product_input):
        super().post_process_product_input(process_product_input_res, product_input)
        product_id = process_product_input_res["create_product"]["id"]
        self.update_product_theme_template(product_id, "shoes")


class BlossomClientBags(BlossomClient):
    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("b"),
            tags=string.ascii_lowercase.index("c"),
            price=string.ascii_lowercase.index("e"),
            description=string.ascii_lowercase.index("g"),
            product_care=string.ascii_lowercase.index("i"),
            material=string.ascii_lowercase.index("j"),
            size_text=string.ascii_lowercase.index("k"),
            made_in=string.ascii_lowercase.index("l"),
        )

    def option1_attr_column_map(self):
        option1_attrs = {"Color": string.ascii_lowercase.index("m")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("n"),
            sku=string.ascii_lowercase.index("o"),
            stock=string.ascii_lowercase.index("p"),
        )
        return option1_attrs

    def option2_attr_column_map(self):
        return {}


def main():
    client = BlossomClient()
    for pi in client.product_inputs_by_sheet_name("clothes(drop5)"):
        print(client.get_tags(pi))


if __name__ == "__main__":
    main()
