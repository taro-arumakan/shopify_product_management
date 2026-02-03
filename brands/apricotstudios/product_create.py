import logging
from brands.apricotstudios.client import ApricotStudiosClient

logging.basicConfig(level=logging.INFO)

# def parse_a_size_line(size_line):
#     pattern = re.compile(r"(\S+?)：([\d.]+(?: cm)?)")
#     if not (size := pattern.findall(size_line)):
#         return ("サイズ", size_line.replace("サイズ ", "").strip())
#     return size[0]


# def parse_table_text_to_html(table_text):
#     table_text_all_sizes = filter(None, table_text.split("\n\n"))
#     header_value_pairs = []
#     for tt in table_text_all_sizes:
#         header_value_pairs.append([parse_a_size_line(line) for line in tt.split("\n")])
#     headers = [""] + [p[0] for p in header_value_pairs[0][1:]]
#     values = [[p[1] for p in pairs] for pairs in header_value_pairs]
#     return utils.Client.generate_table_html(headers, values)


def main():
    client = ApricotStudiosClient(
        "gid://shopify/Product/9181957095680", "1jOg_no7MS8tGwMLKvOpodPg58nWKXSgX"
    )
    sheet_name = "[Spring] 2/25"
    client.sanity_check_sheet(sheet_name)
    # client.process_sheet_to_products(
    #     sheet_name, additional_tags=["25_autumn_2nd", "New Arrival"]
    # )


if __name__ == "__main__":
    main()
