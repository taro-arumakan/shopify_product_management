import logging
import re

logger = logging.getLogger(__name__)


class ProductCreate:
    """
    A class to handle GraphQL queries related to products creation in Shopify, inherited by the ShopifyGraphqlClient class.
    """

    def product_create_default_variant(
        self,
        title,
        description_html,
        vendor,
        tags,
        price,
        sku,
        handle=None,
        status="DRAFT",
        template_suffix=None,
        metafields=None,
    ):
        query = """
        mutation productSet($input: ProductSetInput!) {
            productSet(synchronous: true, input: $input) {
                product {
                    id
                    title
                    handle
                    tags
                    vendor
                    status
                    templateSuffix
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """
        variables = {
            "input": {
                "title": title,
                "descriptionHtml": description_html,
                "vendor": vendor,
                "tags": tags,
                "status": status,
                "productOptions": [
                    {"name": "Title", "values": [{"name": "Default Title"}]}
                ],
                "variants": [
                    {
                        "price": price,
                        "compareAtPrice": price,
                        "sku": sku,
                        "taxable": True,
                        "position": 1,
                        "optionValues": [
                            {"optionName": "Title", "name": "Default Title"}
                        ],
                    }
                ],
            }
        }
        if handle:
            variables["input"]["handle"] = handle
        if template_suffix:
            variables["input"]["templateSuffix"] = template_suffix
        if metafields:
            variables["input"]["metafields"] = metafields

        res = self.run_query(query, variables)
        if errors := res["productSet"]["userErrors"]:
            raise RuntimeError(f"Product creation failed: {errors}")
        return res["productSet"]["product"]

    def product_create(
        self,
        title,
        description_html,
        vendor,
        tags,
        handle=None,
        status="DRAFT",
        template_suffix=None,
        metafields=None,
        option_dicts=None,
    ):
        query = """
        mutation productSet($input: ProductSetInput!) {
            productSet(synchronous: true, input: $input) {
                product {
                    id
                    title
                    handle
                    tags
                    vendor
                    status
                    templateSuffix
                    variants(first: 20) {
                        nodes {
                            id
                            title
                            sku
                        }
                    }
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """
        variables = {
            "input": {
                "title": title,
                "descriptionHtml": description_html,
                "vendor": vendor,
                "tags": tags,
                "status": status,
            }
        }
        if handle:
            variables["input"]["handle"] = handle
        if template_suffix:
            variables["input"]["templateSuffix"] = template_suffix
        if metafields:
            variables["input"]["metafields"] = metafields
        if option_dicts:
            variables["input"]["productOptions"] = self.populate_product_options(
                option_dicts
            )
            variables["input"]["variants"] = self.populate_variant_inputs(option_dicts)

        res = self.run_query(query, variables)
        if errors := res["productSet"]["userErrors"]:
            raise RuntimeError(f"Product creation failed: {errors}")
        return res["productSet"]["product"]

    def populate_product_options(self, option_dicts):
        product_options = {}
        for option in option_dicts:
            option_dict = option["option_values"]
            for k, v in option_dict.items():
                if v not in product_options.get(k, []):
                    product_options.setdefault(k, []).append(v)
        return [
            {"name": k, "position": i + 1, "values": [{"name": vv} for vv in v]}
            for i, (k, v) in enumerate(product_options.items())
        ]

    def populate_variant_inputs(self, option_dicts):
        """
        options_dicts shape:
        [{'option_values': {'カラー': 'PINK', 'サイズ': '2'}, 'price': 35200, 'sku': 'ALV-90154-PK-2', 'stock': 2},
         {'option_values': {'カラー': 'PINK', 'サイズ': '3'}, 'price': 35200, 'sku': 'ALV-90154-PK-3', 'stock': 2},
         {'option_values': {'カラー': 'PINK', 'サイズ': '4'}, 'price': 35200, 'sku': 'ALV-90154-PK-4', 'stock': 2},
         {'option_values': {'カラー': 'INK BLACK', 'サイズ': '2'}, 'price': 35200, 'sku': 'ALV-90154-BK-2', 'stock': 2},
         {'option_values': {'カラー': 'INK BLACK', 'サイズ': '3'}, 'price': 35200, 'sku': 'ALV-90154-BK-3', 'stock': 2},
         {'option_values': {'カラー': 'INK BLACK', 'サイズ': '4'}, 'price': 35200, 'sku': 'ALV-90154-BK-4', 'stock': 2}]
        """
        return [
            {
                "price": option_dict["price"],
                "compareAtPrice": option_dict["price"],
                "sku": option_dict["sku"],
                "taxable": True,
                "position": i + 1,
                "optionValues": [
                    {"optionName": option_name, "name": option_value}
                    for option_name, option_value in option_dict[
                        "option_values"
                    ].items()
                ],
            }
            for i, option_dict in enumerate(option_dicts)
        ]

    def escape_html(self, text):
        replace_map = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;",
            "\n": "<br>",
        }
        for k, v in replace_map.items():
            text = text.replace(k, v)
        return text

    @staticmethod
    def formatted_size_text_to_html_table(size_text):
        """
        [0] 着丈 84 / 肩幅 xxx / 袖丈 yyy
        [1] 着丈 90 / 肩幅 xxx / 袖丈 yyy
        [2] 着丈 90 / 肩幅 xxx / 袖丈 yyy
        [3] 着丈 90 / 肩幅 xxx / 袖丈 yyy
        [4] 着丈 90 / 肩幅 xxx / 袖丈 yyy
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
                header, value = header_value_expression.match(
                    header_value_pair.strip()
                ).groups()
                if header.strip() not in headers:
                    headers.append(header.strip())
                row_values.append(value.strip())
            rows.append(row_values)
        return ProductCreate.generate_table_html(headers, rows)

    @staticmethod
    def get_size_table_html(size_text):
        kv_pairs = list(map(str.strip, re.split("[\n/]", size_text)))
        headers, values = zip(*[kv_pair.split(" ") for kv_pair in kv_pairs])
        return ProductCreate.generate_table_html(headers, values)

    @staticmethod
    def generate_table_html(headers, rows):
        spaces = "            "
        html = """
            <table border="1" style="border-collapse: collapse;" class="size-table">
              <thead>
                <tr>""".replace(
            spaces, ""
        )

        for header in headers:
            html += f"""
                  <th>{header}</th>""".replace(
                spaces, ""
            )

        html += """
                </tr>
              </thead>
              <tbody>""".replace(
            spaces, ""
        )

        for row in rows:
            html += """
                <tr>""".replace(
                spaces, ""
            )
            for v in row:
                html += f"""
                  <td>{v}</td>""".replace(
                    spaces, ""
                )
            html += """
                </tr>""".replace(
                spaces, ""
            )

        html += """
              </tbody>
            </table>""".replace(
            spaces, ""
        )

        return html

    def get_description_html(
        self,
        description,
        product_care,
        material,
        size_text,
        made_in,
        get_size_table_html_func=None,
    ):
        description = self.escape_html(description)
        product_care = self.escape_html(product_care)
        material = self.escape_html(material)
        made_in = self.escape_html(made_in)
        size_table = (get_size_table_html_func or self.get_size_table_html)(size_text)

        description_html = product_description_template()
        description_html = description_html.replace("${DESCRIPTION}", description)
        description_html = description_html.replace("${PRODUCTCARE}", product_care)
        description_html = description_html.replace("${SIZE_TABLE}", size_table)
        description_html = description_html.replace("${MATERIAL}", material)
        description_html = description_html.replace("${MADEIN}", made_in)

        return description_html


def product_description_template():
    return """<!DOCTYPE html>
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

</html>"""
