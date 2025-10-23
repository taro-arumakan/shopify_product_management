import logging
import string
from brands.brandclientbase import BrandClientBase


logger = logging.getLogger(__name__)


class AlvanaClient(BrandClientBase):

    SHOPNAME = "alvanas"
    VENDOR = "alvana"
    LOCATIONS = ["Jingumae"]
    PRODUCT_SHEET_START_ROW = 1

    def product_attr_column_map(self):
        return dict(
            title=string.ascii_lowercase.index("b"),
            tags=string.ascii_lowercase.index("d"),
            price=string.ascii_lowercase.index("e"),
            description=string.ascii_lowercase.index("f"),
            product_care=string.ascii_lowercase.index("g"),
            material=string.ascii_lowercase.index("h"),
            size_text=string.ascii_lowercase.index("i"),
            weight=string.ascii_lowercase.index("j"),
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

    def get_description_html(self, product_info):
        description_html = product_description_template()
        description_html = description_html.replace(
            "${DESCRIPTION}", product_info["description"].replace("\n", "<br>")
        )
        description_html = description_html.replace(
            "${MATERIAL}", product_info["material"]
        )
        description_html = description_html.replace(
            "${MADEIN}", product_info["made_in"]
        )
        return description_html

    def get_tags(self, product_info):
        return product_info["tags"]

    def post_create_a_product(self, create_a_product_res, product_info):
        product_id = create_a_product_res[0]["id"]
        skus = [v["sku"] for v in create_a_product_res[0]["variants"]["nodes"]]
        self.update_metafields(product_id, product_info)
        self.update_weight(skus, product_info)
        return product_id

    def update_metafields(self, product_id, product_info):
        logger.info(f'updating metafields for {product_info["title"]}')
        size_text = product_info["size_text"]
        size_table_html = self.formatted_size_text_to_html_table(size_text)
        if self.to_add_disclaimer_html(product_info["title"]):
            size_table_html += "<br>"
            size_table_html += "<p>注: 製造後に洗い加工を施しているため、記載されているサイズに若干の誤差が生じる場合がございます。</p>"
        self.update_size_table_html_metafield(product_id, size_table_html)
        product_care = self.text_to_simple_richtext(product_info["product_care"])
        self.update_product_care_metafield(product_id, product_care)

    def to_add_disclaimer_html(self, title):
        return title.startswith("NATURAL TWILL") or title in [
            "FADE CENTER SEAM S/S TEE SHIRTS",
            "BHARAT DENIM JACKET",
        ]

    def update_weight(self, skus, product_info):
        weight = product_info.get("weight")
        if weight:
            for sku in skus:
                self.update_inventory_item_weight_by_sku(sku, weight, unit="KILOGRAMS")


def product_description_template():
    return r"""<!DOCTYPE html>
<html><body>
  <div id="alvanaProduct">
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
</body>
</html>"""
