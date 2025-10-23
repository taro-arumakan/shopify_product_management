import logging
import string
from helpers.client import Client
from utils import credentials

logger = logging.getLogger(__name__)


class AlvanaClient(Client):

    def __init__(self):
        cred = credentials("alvanas")
        super().__init__(
            shop_name=cred.shop_name,
            access_token=cred.access_token,
            google_credential_path=cred.google_credential_path,
            sheet_id=cred.google_sheet_id,
        )
        self.vendor = "alvana"
        self.locations = ["Jingumae"]

    def product_info_list_from_sheet(self, sheet_name):
        start_row = 1
        column_product_attrs = dict(
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
        option1_attrs = {"カラー": string.ascii_lowercase.index("l")}
        option1_attrs.update(
            drive_link=string.ascii_lowercase.index("m"),
        )
        option2_attrs = {"サイズ": string.ascii_lowercase.index("n")}
        option2_attrs.update(
            sku=string.ascii_lowercase.index("o"),
            stock=string.ascii_lowercase.index("p"),
        )
        return self.to_products_list(
            self.sheet_id,
            sheet_name,
            start_row,
            column_product_attrs,
            option1_attrs,
            option2_attrs,
        )

    def sanity_check_product_info_list(self, product_info_list):
        super().sanity_check_product_info_list(
            product_info_list, self.formatted_size_text_to_html_table
        )

    def to_add_disclaimer_html(self, title):
        return title.startswith("NATURAL TWILL") or title in [
            "FADE CENTER SEAM S/S TEE SHIRTS",
            "BHARAT DENIM JACKET",
        ]

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

    def update_weight(self, skus, product_info):
        weight = product_info.get("weight")
        if weight:
            for sku in skus:
                self.update_inventory_item_weight_by_sku(sku, weight, unit="KILOGRAMS")

    def create_a_product(self, product_info):
        logger.info(f'creating {product_info["title"]}')
        description_html = self.get_description(
            product_info["description"],
            product_info["material"],
            product_info["made_in"],
        )
        tags = product_info["tags"]
        res = super().create_a_product(
            product_info, self.vendor, description_html, tags, self.locations
        )
        product_id = res[0]["id"]
        skus = [v["sku"] for v in res[0]["variants"]["nodes"]]
        self.update_metafields(product_id, product_info)
        self.update_weight(skus, product_info)
        return product_id

    def get_description(self, product_description, material, made_in):
        description_html = product_description_template()
        description_html = description_html.replace(
            "${DESCRIPTION}", product_description.replace("\n", "<br>")
        )
        description_html = description_html.replace("${MATERIAL}", material)
        description_html = description_html.replace("${MADEIN}", made_in)
        return description_html

    def update_stocks(self, product_info_list):
        super().update_stocks(product_info_list, self.locations[0])


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
