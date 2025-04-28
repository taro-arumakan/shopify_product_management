import logging
import re

class ProductCreate:
    """
    A class to handle GraphQL queries related to products creation in Shopify, inherited by the ShopifyGraphqlClient class.
    """
    logger = logging.getLogger(f"{__module__}.{__qualname__}")

    def product_create_default_variant(self, title, description_html, vendor, tags, price, sku, handle=None, status='DRAFT', template_suffix=None, metafields=None):
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
                "productOptions": [{
                    'name': 'Title',
                    'values': [{'name': "Default Title"}]
                }],
                "variants": [{
                    'price': price,
                    'sku': sku,
                    'taxable': True,
                    'position': 1,
                    "optionValues": [
                        {
                            "optionName": "Title",
                            "name": "Default Title"
                        }
                    ]
                }]
            }
        }
        if handle:
            variables["input"]["handle"] = handle
        if template_suffix:
            variables["input"]["templateSuffix"] = template_suffix
        if metafields:
            variables["input"]["metafields"] = metafields

        res = self.run_query(query, variables)
        if errors := res['productSet']['userErrors']:
            raise RuntimeError(f"Product creation failed: {errors}")
        return res['productSet']['product']

    def product_create(self, title, description_html, vendor, tags, handle=None, status='DRAFT', template_suffix=None, metafields=None, option_lists=None):
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
            }
        }
        if handle:
            variables["input"]["handle"] = handle
        if template_suffix:
            variables["input"]["templateSuffix"] = template_suffix
        if metafields:
            variables["input"]["metafields"] = metafields
        if option_lists:
            variables["input"]["productOptions"] = self.populate_product_options(option_lists)
            variables["input"]["variants"] = self.populate_variant_inputs(option_lists)

        res = self.run_query(query, variables)
        if errors := res['productSet']['userErrors']:
            raise RuntimeError(f"Product creation failed: {errors}")
        return res['productSet']['product']

    def populate_product_options(self, option_lists):
        product_options = {}
        for option_dict, _, _ in option_lists:
            for k, v in option_dict.items():
                if v not in product_options.get(k, []):
                    product_options.setdefault(k, []).append(v)
        return [{'name': k,
                 'position': i+1,
                 'values': [{'name': vv} for vv in v]
                } for i, (k, v) in enumerate(product_options.items())]

    def populate_variant_inputs(self, option_lists):
        """
        option_lists shape:
        [[{'カラー': 'Black', 'サイズ': 'S'}, 23100, 'OVBAX25107BLK-S'],
         [{'カラー': 'Black', 'サイズ': 'M'}, 23100, 'OVBAX25107BLK-M'],
         [{'カラー': 'Beige', 'サイズ': 'S'}, 23100, 'OVBAX25107BEE-S'],
         [{'カラー': 'Beige', 'サイズ': 'M'}, 23100, 'OVBAX25107BEE-M']]

        [[{'カラー': 'Black'}, 23100, 'OVBAX25107BLK'],
         [{'カラー': 'Beige'}, 23100, 'OVBAX25107BEE']]
        """
        return [{'price': price,
                 'sku': sku,
                 'taxable': True,
                 'position': i+1,
                 'optionValues': [
                     {'optionName': option_name,
                      'name': option_value}
                     for option_name, option_value in options_dict.items()
                 ]}
                for i, (options_dict, price, sku) in enumerate(option_lists)]

    def escape_html(self, text):
        replace_map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;',
            '\n': '<br>',
        }
        for k, v in replace_map.items():
            text = text.replace(k, v)
        return text

    @staticmethod
    def get_size_table_html(size_text):
        kv_pairs = list(map(str.strip, re.split('[\n/]', size_text)))
        headers, values = zip(*[kv_pair.split(' ') for kv_pair in kv_pairs])
        return ProductCreate.generate_table_html(headers, values)

    @staticmethod
    def generate_table_html(headers, rows):
        spaces = '            '
        html = """
            <table border="1" style="border-collapse: collapse; text-align: left;">
              <thead>
                <tr>""".replace(spaces, '')

        for header in headers:
            html += """
                  <th>{header}</th>""".replace(spaces, '')

        html += """
                </tr>
              </thead>
              <tbody>""".replace(spaces, '')

        for row in rows:
            html += """
                <tr>""".replace(spaces, '')
            for v in row:
                html += f"""
                  <td>{v}</td>""".replace(spaces, '')
            html += """
                </tr>""".replace(spaces, '')

        html += """
              </tbody>
            </table>""".replace(spaces, '')

        return html

    def get_description_html(self, description, product_care, material, size_text, made_in, get_size_table_html_func=None):
        description = self.escape_html(description)
        product_care = self.escape_html(product_care)
        material = self.escape_html(material)
        made_in = self.escape_html(made_in)
        size_table = (get_size_table_html_func or self.get_size_table_html)(size_text)

        description_html = product_description_template()
        description_html = description_html.replace('${DESCRIPTION}', description)
        description_html = description_html.replace('${PRODUCTCARE}', product_care)
        description_html = description_html.replace('${SIZE_TABLE}', size_table)
        description_html = description_html.replace('${MATERIAL}', material)
        description_html = description_html.replace('${MADEIN}', made_in)

        return description_html

    def product_variants_bulk_create(self, product_id, variants):
        query = """
        mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
            productVariantsBulkCreate(productId: $productId, variants: $variants) {
                productVariants {
                    id
                    title
                    selectedOptions {
                        name
                        value
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
            "productId": product_id,
            "variants": variants
        }
        res = self.run_query(query, variables)
        if errors := res['productVariantsBulkCreate']['userErrors']:
            raise RuntimeError(f"Product variants creation failed: {errors}")
        return res['productVariantsBulkCreate']['productVariants']


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
