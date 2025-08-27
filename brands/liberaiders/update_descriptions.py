import string
import utils
from brands.alvana.size_text_to_html_table import size_text_to_html_table


def get_description(product_description, material):
    description_html = product_description_template()
    description_html = description_html.replace(
        "${DESCRIPTION}", product_description.replace("\n", "<br>")
    )
    description_html = description_html.replace("${MATERIAL}", material)
    # description_html = description_html.replace("${MADEIN}", made_in)
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
    client = utils.client("liberaiders")
    rows = client.worksheet_rows(client.sheet_id, "Product Master")

    for row in rows[1:]:
        title = row[1].strip()
        product_description = row[string.ascii_uppercase.index("F")].strip()
        if not (title and product_description):
            continue
        print(f"processing {title}")
        product_id = client.product_id_by_title(title)
        # size_text_ja = row[string.ascii_uppercase.index("I")].strip()
        # if size_text_ja:
        #     size_table_html_ja = size_text_to_html_table(size_text_ja)
        #     res = client.update_size_table_html_ja_metafield(
        #         product_id, size_table_html_ja
        #     )
        #     print(res)
        # size_text_en = row[string.ascii_uppercase.index("J")].strip()
        # if size_text_en:
        #     size_table_html_en = size_text_to_html_table(size_text_en)
        #     res = client.update_size_table_html_en_metafield(
        #         product_id, size_table_html_en
        #     )
        #     print(res)

        # made_in = row[string.ascii_uppercase.index("I")].strip()
        material = row[string.ascii_uppercase.index("H")].strip()
        res = client.update_product_description(
            product_id, get_description(product_description, material)
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
      </tbody>
    </table>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
