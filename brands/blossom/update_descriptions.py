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


def main():
    client = utils.client("blossomhcompany")
    rows = client.worksheet_rows(client.sheet_id, "clothes")

    for row in rows[7:]:
        title = row[0].strip()
        if not title:
            continue
        print(f"processing {title}")
        product_id = client.product_id_by_title(title)
        if product_description := row[string.ascii_uppercase.index("F")].strip():
            made_in = row[string.ascii_uppercase.index("K")].strip()
            material = row[string.ascii_uppercase.index("I")].strip()
            res = client.update_product_description(
                product_id, get_description(product_description, material, made_in)
            )
            print(res)
        if product_care := row[string.ascii_uppercase.index("H")].strip():
            res = client.update_product_care_metafield(
                product_id, client.text_to_simple_richtext(product_care)
            )
            print(res)
        if size_text := row[string.ascii_uppercase.index("J")].strip():
            size_table_html = client.formatted_size_text_to_html_table(size_text)
            res = client.update_size_table_html_metafield(product_id, size_table_html)
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
</body>
</html>"""


if __name__ == "__main__":
    main()
