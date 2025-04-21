def size_table_html_from_size_dict(size_text_dict):
    rows = []
    headers = ['']

    for size, size_text in size_text_dict.items():
        row_values = [size]
        header_values = size_text.split('\n')

        for header_value in header_values:
            header, value = header_value.split('：')
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
