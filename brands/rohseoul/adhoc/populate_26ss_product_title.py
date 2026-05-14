import json
import re
import pathlib
import utils
from brands.rohseoul.publish_lookbook_article import populate_lookbook_products_dicts

client = utils.client("rohseoul")
lookbook_products_dict = populate_lookbook_products_dicts(
    client, "17tfWLDl6rcewWnwULPEz5nA7TVLz1ShEuKgILnP7xa4", "LOOKBOOK - SPRING 26"
)
path = (
    f"{pathlib.Path.home()}/sc/rohseoul/templates/article.lookbook-lookbook-26-ss.json"
)


def populate_product_content(title):
    products = lookbook_products_dict[title]
    ress = []
    for product, link in products:
        res = "<p>"
        if link:
            res += f'<a href="{link}">'
        res += f"{product}"
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


if __name__ == "__main__":
    main()
