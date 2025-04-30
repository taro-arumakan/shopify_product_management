import re
import utils

SHOPNAME = 'apricot-studios'

def is_digit(s):
    try:
        float(s.replace('mm', ''))
        return True
    except ValueError:
        return False

def convert_to_html_table(header_text, rows_text):
    header_text = header_text.strip()
    category = ''

    headers = re.split(r'\s{2,}', header_text.strip())
    rows = [r.strip() for r in rows_text.split('\n') if r.strip()]
    first_row_values = re.split(r'\s+', rows[0])
    values_length = len([v for v in first_row_values[1:] if is_digit(v)])

    if len(headers) > values_length:
        assert len(headers) == values_length + 1, 'length of the headers and row values does not agree'
        category = headers[0]
        headers = headers[1:]

    if len(headers) < len(first_row_values):
        headers = [""] + headers

    table_html = f"<table border='1'><thead><tr>"
    table_html += "".join(f"<th>{header}</th>" for header in headers)
    table_html += "</tr></thead><tbody>"

    for row in rows:
        values = re.split(r"\s+", row.strip())
        table_html += "<tr>" + "".join(f"<td>{value}</td>" for value in values) + "</tr>"
    table_html += "</tbody></table>"
    return category, table_html


def text_to_html_tables_and_paragraphs(text):
    text = '\n'.join(p.strip() for p in text.replace('　', '  ').split('\n')) + '\n'

    table_expression = re.compile(r"(.*\n)((?:[\S\d]+\s+[\d\.\sm]*\n)+)$", re.MULTILINE)
    table_matches = table_expression.findall(text)

    # Remove matched tables from the text
    remaining_text = table_expression.sub("", text).strip()

    # Treat remaining text as additional paragraphs
    paragraphs = [p.strip() for p in remaining_text.split("\n") if p.strip()]

    html_output = ""

    for match in table_matches:
        try:
            category, table_html = convert_to_html_table(match[0], match[1])
        except AssertionError as e:
            print(f"!!!! Error: {e}")
            continue

        header = f'<h4>{category}</h4>' if len(table_matches) > 1 else ''
        html_output += f"{header}{table_html}\n\n"

    # Append the paragraphs as <p> elements
    for paragraph in paragraphs:
        paragraph = paragraph.split()
        if paragraph:
            html_output += f"<p>{' '.join(paragraph)}</p>\n"
    return html_output

def update_size_table_html_metafield(client:utils.Client, title, size_table_html):
    product_id = client.product_id_by_title(title)
    return client.update_size_table_html_metafield(product_id, size_table_html)

def main():
    client = utils.client(SHOPNAME)
    rows = client.worksheet_rows(client.sheet_id, 'Product Master')

    for row in rows[1:]:
        title = row[1].strip()
        if not title:
          continue
        print(f'processing {title}')
        size_text = row[12]
        if not size_text:
            continue

        size_table_html = text_to_html_tables_and_paragraphs(size_text)
        print(size_table_html)
        product_id = client.product_id_by_title(title)
        res = client.update_size_table_html_metafield(product_id, size_table_html)
        print(res)
        break
    print('done updating')

if __name__ == '__main__':
    main()
