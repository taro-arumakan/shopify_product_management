import functools
import json
import pathlib
import re

import utils
from brands.rohseoul.publish_lookbook_article import populate_lookbook_products_dicts

client = utils.client("rohseoul")
lookbook_products_dict = populate_lookbook_products_dicts(
    client, "17tfWLDl6rcewWnwULPEz5nA7TVLz1ShEuKgILnP7xa4", "LOOKBOOK - SPRING 26"
)
path = (
    f"{pathlib.Path.home()}/sc/rohseoul/templates/article.lookbook-lookbook-26-ss.json"
)


def variant_color(variant):
    for so in variant["selectedOptions"]:
        if so["name"] == "カラー":
            return so["value"]


@functools.lru_cache(maxsize=128)
def products_by_title_cached(product_title):
    return client.products_by_query(f"""title:"{product_title}" AND status:'ACTIVE'""")


@functools.lru_cache(maxsize=128)
def lookup_product_variant_url(product_and_color):
    # Pattern explanation:
    # ^(.*)         -> Group 1: Matches everything from the start (greedy)
    # \s+           -> Matches the whitespace separator
    # ([A-Z].*)     -> Group 2: Matches a capital letter followed by anything to the end
    pattern = r"^(.*)\s+([A-Z].*)$"

    match = re.search(pattern, product_and_color)
    if match:
        title = match.group(1)
        color = match.group(2)
        print(f"Title: {title} | Color: {color}")
        products = products_by_title_cached(title)
        for p in products:
            for v in p["variants"]["nodes"]:
                if variant_color(v).lower() == color.lower():
                    return f"https://rohseoul.jp/products/{p['handle']}?variant={v['id'].rsplit("/", 1)[-1]}"


def populate_product_content(section_title):
    products = lookbook_products_dict[section_title]
    ress = []
    for product_title, link in products:
        res = "<p>"
        link = link or lookup_product_variant_url(product_title)
        if link:
            res += f'<a href="{link}">'
        res += f"{product_title}"
        if link:
            res += "</a>"
        res += "</p>"
        ress.append(res)
    return "".join(ress)


def main():
    with open(path) as f:
        content = f.read()
        # Remove C-style comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        d = json.loads(content)

    for k, v in d["sections"].items():
        if k.startswith("multi_column"):
            for t, block in v["blocks"].items():
                if (
                    block_number := block["settings"]["title"]
                ) in lookbook_products_dict:
                    block["settings"]["content"] = populate_product_content(
                        block_number
                    )

    with open(path, "w") as of:
        of.write(json.dumps(d, indent=2, ensure_ascii=False))


def check():
    for k, v in lookbook_products_dict.items():
        for product_title, _ in v:
            print(product_title)
            print(lookup_product_variant_url(product_title))


if __name__ == "__main__":
    main()
