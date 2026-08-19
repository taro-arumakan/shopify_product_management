import re
import utils
from lxml import html

product_titles_to_ignore = ["SHOPPING BAG", "TUMBLER POUCH"]

description_pattern = re.compile(
    r"(.*?)(<h3>商品説明(?:\s*<br\s*/?>)?\s*</h3>.*?)<h3>その他注意事項</h3>",
    flags=re.DOTALL | re.IGNORECASE,
)


def strip_disclaimers(html_string: str) -> str:
    found = description_pattern.match(html_string)
    assert "こちらの商品は指定日配送を承ることが出来かねます" in found.group(
        1
    ), html_string
    if "<div" in found.group(2):
        assert found.group(2).count("<div") == found.group(2).count("</div>") == 1
    main_fragment = found.group(2).replace("</div>", "")
    main_fragment = re.sub("<div.*?>", "", main_fragment)
    return f"""<div id="cataldesignProduct">{main_fragment}</div>"""


def is_html_valid(html_string: str) -> bool:
    try:
        parser = html.HTMLParser(recover=False)
        html.fromstring(html_string, parser=parser)
        return True
    except html.EtreeError:
        return False


def process(brand):
    client = utils.client(brand)
    products = client.products_by_query(
        "status:'ACTIVE'", additional_fields=["descriptionHtml"]
    )
    products = [
        product
        for product in products
        if product["title"] not in product_titles_to_ignore
    ]

    for product in products:
        print(product["title"])
        new_description = strip_disclaimers(product["descriptionHtml"])
        assert is_html_valid(new_description), product["title"]
        client.update_product_description(product["id"], new_description)


def main():
    for brand in ["gbh", "roh", "kume", "archive"]:
        print(f"processing {brand}")
        process(brand)


if __name__ == "__main__":
    main()
