import re


def size_table_html(size_text):
    rows = []
    headers = []
    row_values = []

    header_values = size_text.split("\n")

    for header_value in header_values:
        header, value = header_value.split("：")
        if header.strip() not in headers:
            headers.append(header.strip())
        row_values.append(value.strip())
    rows.append(row_values)
    return generate_html(headers, rows)


def size_table_html_from_size_dict_space_pairs(size_text_dict):
    """
    着丈 34 ウエスト 34 ヒップ 48 裾幅 31.5 前股上 34cm
    着丈106 ウエスト35.5 ヒップ45 裾幅22 前股上31.5
    """
    rows = []
    headers = [""]
    regx = re.compile(r"([^\d]+)\s*?([\d\.]+)")
    for index, (size, size_text) in enumerate(size_text_dict.items()):
        headers_and_values = regx.findall(size_text)
        if index == 0:
            headers += [header_value[0].strip() for header_value in headers_and_values]
        row_values = [size] + [
            header_value[1].strip() for header_value in headers_and_values
        ]
        rows.append(row_values)
    return generate_html(headers, rows)


def size_table_html_from_size_dict(size_text_dict):
    """
    サイズ：H95 x Ø68mm
    容量：220ml / 7.4oz
    暑さ：0.8mm
    重さ：50g
    """
    rows = []
    headers = [""]

    for size, size_text in size_text_dict.items():
        row_values = [size]
        headers_and_values = size_text.split("\n")

        for header_value in headers_and_values:
            header, value = header_value.split("：")
            if header.strip() not in headers:
                headers.append(header.strip())
            row_values.append(value.strip())
        rows.append(row_values)
    return generate_html(headers, rows)


def generate_html(headers, rows):
    # Generate HTML table
    html = """
<table border="1" style="border-collapse: collapse; text-align: left;">
  <thead>
    <tr>"""

    for header in headers:
        html += f"""
      <th>{header}</th>"""

    html += """
    </tr>
  </thead>
  <tbody>"""

    for row in rows:
        html += """
    <tr>"""
        for v in row:
            html += f"""
      <td>{v}</td>"""
        html += """
    </tr>"""

    html += """
  </tbody>
</table>"""

    return html
