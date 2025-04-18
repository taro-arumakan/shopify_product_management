import string
import utils
from alvana.size_text_to_html_table import size_text_to_html_table

def get_description(product_description, material, made_in):
    description_html = product_description_template()
    description_html = description_html.replace('${DESCRIPTION}', product_description)
    description_html = description_html.replace('${MATERIAL}', material)
    description_html = description_html.replace('${MADEIN}', made_in)
    return description_html


def get_product_care(product_care_text):
    res = {
        'type': 'root',
        'children': [
            {'children': [{'type': 'text', 'value': product_care_text.strip('\"').replace('●', '- ')}], 'type': 'paragraph'},
        ]
    }
    return res

def main():
    client = utils.client('alvanas')
    rows = client.worksheet_rows(client.sheet_id, 'Product Master')

    for row in rows[1:]:
        title = row[1].strip()
        if not title:
          continue
        print(f'processing {title}')
        product_id = client.product_id_by_title(title)
        size_table_html = size_text_to_html_table(row[string.ascii_uppercase.index('H')].strip())
        res = client.update_size_table_html_metafield(product_id, size_table_html)
        print(res)
        product_description = row[string.ascii_uppercase.index('E')].strip()
        made_in = row[string.ascii_uppercase.index('I')].strip()
        material = row[string.ascii_uppercase.index('G')].strip()
        res = client.update_product_description(product_id, get_description(product_description, material, made_in))
        print(res)
        res = client.update_product_care_metafield(product_id, get_product_care(row[string.ascii_uppercase.index('F')].strip()))
        print(res)
    print('done updating')


def product_description_template():
    return r"""<!DOCTYPE html>
<html>

<head>
  <style type="text/css">
    #alvanaProduct h3 {
      margin: 40px 0 16px;
      padding-left: 12px;
      border-left: 3px solid #000000;
      color: #000000;
      text-align: left;
    }

    #alvanaProduct p {
      margin: 8px 0;
      line-height: 1.6em;
    }
    #alvanaProduct table {
      width: 100%;
      margin-top: 16px;
      border-collapse: collapse;
    }
    #alvanaProduct th {
      border: 1px solid #e2e2e2;
      text-align: center;
      padding: 5px;
    }

    #alvanaProduct td {
      border: 1px solid #e2e2e2;
      text-align: center;
      padding: 5px;
    }

    #alvanaProduct tr {
      border: 1px solid #e2e2e2;
    }

    #alvanaProduct .table_title {
      background-color: rgba(18, 18, 18, 0.04);
      font-weight: bold;
    }
  </style>
</head>

<body>
  <div id="alvanaProduct">
    <h3>商品説明</h3>
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

if __name__ == '__main__':
    main()
