import json
import pathlib
import re

import utils
from brands.rohseoul.publish_lookbook_article import (
    populate_lookbook_products_dicts,
    populate_product_content,
)

client = utils.client("rohseoul")


def main():
    lookbook_products_dict = populate_lookbook_products_dicts(
        client, "17tfWLDl6rcewWnwULPEz5nA7TVLz1ShEuKgILnP7xa4", "LOOKBOOK - SUMMER 26"
    )
    path = f"{pathlib.Path.home()}/sc/rohseoul/templates/article.lookbook-lookbook---26-summer.json"

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
                        lookbook_products_dict, *block_number.split("-")
                    )

    with open(path, "w") as of:
        of.write(json.dumps(d, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
