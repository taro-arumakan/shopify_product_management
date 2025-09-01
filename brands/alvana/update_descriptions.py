import string
import utils


def get_description(product_description, material, made_in):
    description_html = product_description_template()
    description_html = description_html.replace(
        "${DESCRIPTION}", product_description.replace("\n", "<br>")
    )
    description_html = description_html.replace("${MATERIAL}", material)
    description_html = description_html.replace("${MADEIN}", made_in)
    return description_html


def get_product_care(product_care_text):
    res = {
        "type": "root",
        "children": [
            {
                "children": [
                    {
                        "type": "text",
                        "value": product_care_text.strip('"').replace("●", "- "),
                    }
                ],
                "type": "paragraph",
            },
        ],
    }
    return res


def main():
    client = utils.client("alvanas")
    rows = client.worksheet_rows(client.sheet_id, "Product Master")

    for row in rows[1:]:
        title = row[1].strip()
        if not title:
            continue
        print(f"processing {title}")
        product_id = client.product_id_by_title(title)
        size_text = row[string.ascii_uppercase.index("H")].strip()
        if size_text:
            size_table_html = client.formatted_size_text_to_html_table(size_text)
            if title.startswith("NATURAL TWILL") or title in [
                "FADE CENTER SEAM S/S TEE SHIRTS",
                "BHARAT DENIM JACKET",
            ]:
                size_table_html += "<br>"
                size_table_html += "<p>注: 製造後に洗い加工を施しているため、記載されているサイズに若干の誤差が生じる場合がございます。</p>"
            res = client.update_size_table_html_metafield(product_id, size_table_html)
            print(res)
        product_description = row[string.ascii_uppercase.index("E")].strip()
        if not product_description.startswith("#N/A"):
            made_in = row[string.ascii_uppercase.index("I")].strip()
            material = row[string.ascii_uppercase.index("G")].strip()
            res = client.update_product_description(
                product_id, get_description(product_description, material, made_in)
            )
            print(res)
        res = client.update_product_care_metafield(
            product_id, get_product_care(row[string.ascii_uppercase.index("F")].strip())
        )
        print(res)
    print("done updating")


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


if __name__ == "__main__":
    main()
