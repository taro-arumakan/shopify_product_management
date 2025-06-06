import re


def size_text_to_html_table(size_text):
    """
    [0] 着丈 84 / 肩幅 xxx / 袖丈 yyy
    [1] 着丈 90 / 肩幅 xxx / 袖丈 yyy
    [2] 着丈 90 / 肩幅 xxx / 袖丈 yyy
    [3] 着丈 90 / 肩幅 xxx / 袖丈 yyy
    [4] 着丈 90 / 肩幅 xxx / 袖丈 yyy
    """
    size_expression = re.compile(r"\[(\w+)\]\s*(.*)")
    header_value_expression = re.compile(r"([^\d]+)\s*([\d\.]+)")

    rows = []
    headers = ["Size"]

    for line in filter(None, size_text.strip().split("\n")):
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
