import logging
import re

import utils

from brands.rohseoul.client import AFTER_SERVICE_HTML

logging.basicConfig(level=logging.INFO)

# Every active product's descriptionHtml has exactly one of these (verified
# against all 143 active products) - a more reliable anchor than the
# preceding 手入れ方法 section, which some older products lack entirely or
# render with a stray <br> before the closing tag.
SIZE_MATERIAL_H3 = re.compile(r"<h3>\s*サイズ・素材\s*</h3>")

# Skip apparel/accessories for now (exhaustive as of 2026-07: exactly these 4
# strings cover every Clothes/Accessories-category product; no other casing
# variant exists). Revisit once the after-service wording is decided for them.
APPAREL_TAGS = {"Clothes", "clothes", "Accessories", "ACC"}

_BALANCE_TAGS = ("div", "h3", "p", "a", "table", "tbody", "tr", "th", "td")


def has_balanced_tags(html_string: str) -> bool:
    """Open/close tag counts match, for the tags this script's insertion touches.
    Not full HTML validation (no HTML parser is a project dependency) - just
    enough to catch a corrupted insertion before writing it to Shopify.
    """
    return all(
        len(re.findall(rf"<{tag}\b", html_string))
        == len(re.findall(rf"</{tag}>", html_string))
        for tag in _BALANCE_TAGS
    )


def insert_after_service_section(description_html: str) -> str:
    if "アフターサービス" in description_html:
        return description_html
    matches = list(SIZE_MATERIAL_H3.finditer(description_html))
    assert (
        len(matches) == 1
    ), f"expected exactly one サイズ・素材 heading, found {len(matches)}"
    idx = matches[0].start()
    return description_html[:idx] + AFTER_SERVICE_HTML + "\n" + description_html[idx:]


def process(dry_run=True):
    client = utils.client("rohseoul")
    products = client.products_by_query(
        "status:'ACTIVE'", additional_fields=["descriptionHtml"]
    )
    updated = skipped_apparel = skipped_done = 0
    for product in products:
        if set(product["tags"]) & APPAREL_TAGS:
            logging.info(f"skip (apparel/accessory): {product['title']}")
            skipped_apparel += 1
            continue
        if "アフターサービス" in product["descriptionHtml"]:
            logging.info(f"skip (already has section): {product['title']}")
            skipped_done += 1
            continue
        new_description = insert_after_service_section(product["descriptionHtml"])
        assert has_balanced_tags(new_description), product["title"]
        logging.info(f"{'[DRY] ' if dry_run else ''}updating {product['title']}")
        if not dry_run:
            client.update_product_description(product["id"], new_description)
        updated += 1
    logging.info(
        f"done: updated={updated} skipped_apparel={skipped_apparel} "
        f"skipped_already_done={skipped_done} dry_run={dry_run}"
    )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Insert the アフターサービス (warranty) section into active "
        "ROH Seoul product descriptions."
    )
    parser.add_argument(
        "--apply", action="store_true", help="Write changes (default: dry-run)."
    )
    args = parser.parse_args()
    process(dry_run=not args.apply)


if __name__ == "__main__":
    main()
