"""Store-wide pass: ensure every ACTIVE alvana product's size_table_html has an English
`en` translation (Japanese headers stay on the base value). Translates the existing base
table's headers and wash disclaimer to English and registers it as the en translation.
Does NOT modify the base value.

Run after brands/alvana/update_size_field.py (which rebuilds the 26 S/S base tables)."""

import re
import utils
from brands.alvana.update_size_field import (
    DISCLAIMER_EN,
    DISCLAIMER_JA,
    header_for,
    register_en_translation,
)

client = utils.client("alvana")

DRY_RUN = True


def translate_size_table_html(base_html):
    """Return the English size table for a Japanese base: translate every <th> (except
    'Size') and swap the wash disclaimer. Numbers and structure are untouched."""

    def th(mo):
        label = mo.group(1)
        return mo.group(0) if label == "Size" else f"<th>{header_for(label, 'en')}</th>"

    return re.sub(r"<th>(.*?)</th>", th, base_html).replace(
        DISCLAIMER_JA, DISCLAIMER_EN
    )


def main():
    active = [
        p
        for p in client.products_by_query("")
        if p["status"] == "ACTIVE" and "(no image)" not in p["title"]
    ]
    done, skipped = 0, 0
    for p in active:
        mfs = [
            m
            for m in p["metafields"]["nodes"]
            if m["key"] == "size_table_html" and m["value"]
        ]
        if not mfs:
            continue
        mf = mfs[0]
        try:
            en_html = translate_size_table_html(mf["value"])
        except KeyError as e:
            skipped += 1
            print(f"SKIP {p['title']}: {e}")
            continue

        done += 1
        ja_h = [h for h in re.findall(r"<th>(.*?)</th>", mf["value"]) if h != "Size"]
        en_h = [h for h in re.findall(r"<th>(.*?)</th>", en_html) if h != "Size"]
        disc = " (+disclaimer)" if DISCLAIMER_JA in mf["value"] else ""
        print(f"{p['title'][:46]:46s} {ja_h} -> {en_h}{disc}")
        if not DRY_RUN:
            register_en_translation(mf["id"], en_html)

    print(
        f"\n{'DRY RUN — ' if DRY_RUN else ''}{done} en translations, {skipped} skipped"
    )


if __name__ == "__main__":
    main()
