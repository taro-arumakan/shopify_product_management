import re
import utils

client = utils.client("alvana")

# Source: "alvana 26 S/S サイズ表"
SHEET_ID = "1l4RmXLPSeuLu9b2HY7oelKEyiPfaf1Wi7pFdb5rA614"
SHEET_TAB = "パターンNo入"

# When True, only print what would be written; no metafield/translation is changed.
DRY_RUN = True

# Sheet 型番 -> Shopify product SKU prefix (fix typos / zero padding).
product_sku_map = {"ALV-0177": "ALV-00177"}

# Measurement-row columns E..H map to size options ①②③④ -> 1..4.
SIZE_COLS = {4: "1", 5: "2", 6: "3", 7: "4"}

# Localized model: the ja (base) size_table_html keeps Japanese headers; the en
# translation carries the English headers. CB/NP/BC qualifiers are stripped first.
LABEL_TRANSLATION = {
    "着丈": "Length",
    "身巾": "Width",
    "身幅": "Width",
    "肩幅": "Shoulder",
    "袖丈": "Sleeve",
    "ゆき丈": "Sleeve",
    "裄丈": "Sleeve",
    "ウエスト": "Waist",
    "ヒップ": "Hip",
    "股上": "Rise",
    "股下": "Inseam",
    "裾巾": "Hem",
    "裾幅": "Hem",
    "頭周最大": "Head Circumference",
}

# Per-product measurement-method note (ja base / en translation), keyed by the CB/NP/BC
# suffix the source used for 着丈 / 袖丈. Headers stay clean; this note explains the method.
MEASUREMENT_NOTES = {
    "CB": (
        "着丈CB / 着丈BC: 後ろ襟の真ん中から裾までの長さで計測しています。",
        "Length (CB/BC): measured from the center of the back neck (collar) down to the hem.",
    ),
    "NP_len": (
        "着丈NP: 首の付け根（肩との境目）から裾までの長さで計測しています。",
        "Length (NP): measured from the base of the neck (where it meets the shoulder) down to the hem.",
    ),
    "NP_sleeve": (
        "袖丈NP: 首の横の付け根（肩のライン）から、肩のトップを通って袖先までの長さで計測しています。「肩の切り替えからの袖丈」とは異なります。",
        "Sleeve (NP): measured from the side base of the neck (shoulder line), over the shoulder point, to the cuff — note this differs from a sleeve length taken from the shoulder seam.",
    ),
}
NOTE_ORDER = ["CB", "NP_len", "NP_sleeve"]


def measurement_methods(labels):
    methods = set()
    for lab in labels:
        if lab.startswith("着丈") and ("CB" in lab or "BC" in lab):
            methods.add("CB")
        if lab.startswith("着丈") and "NP" in lab:
            methods.add("NP_len")
        if lab.startswith("袖丈") and "NP" in lab:
            methods.add("NP_sleeve")
    return methods


def method_note_html(methods, lang):
    idx = 0 if lang == "ja" else 1
    lines = [MEASUREMENT_NOTES[m][idx] for m in NOTE_ORDER if m in methods]
    return "".join(f"<p>{l}</p>" for l in lines)


DISCLAIMER_JA = "注: 製造後に洗い加工を施しているため、記載されているサイズに若干の誤差が生じる場合がございます。"
DISCLAIMER_EN = (
    "Note: This item is washed after production, so the actual measurements may "
    "vary slightly from those listed."
)

EMPTY_VALUES = ("", "-")


def clean_label(label):
    """Drop the CB / NP / BC measurement-point qualifiers, with or without parens
    (e.g. 着丈CB or 着丈(CB) -> 着丈)."""
    return re.sub(r"[(（]?(CB|NP|BC)[)）]?$", "", label.strip()).strip()


def header_for(label, lang):
    """Japanese (cleaned) header for the base value, English for the en translation.
    Already-English headers pass through unchanged."""
    cleaned = clean_label(label)
    if lang == "ja":
        return cleaned
    if cleaned in LABEL_TRANSLATION:
        return LABEL_TRANSLATION[cleaned]
    if cleaned in set(LABEL_TRANSLATION.values()):
        return cleaned
    raise KeyError(f"no English translation for {cleaned!r} (raw {label!r})")


def parse_blocks():
    """Each product is a block: a 型番 row (col A) followed by measurement rows
    (label in col D, size values in cols E..H). Returns
    [{"sku": 型番, "meas": [(label, {size: value})]}]."""
    rows = client.worksheet_rows(SHEET_ID, SHEET_TAB)
    blocks, cur = [], None
    for r in rows[3:]:

        def cell(i):
            return str(r[i]).strip() if len(r) > i else ""

        if cell(0).startswith("ALV"):
            cur = {"sku": cell(0), "meas": []}
            blocks.append(cur)
        if cur and cell(3):
            cur["meas"].append(
                (cell(3), {sz: cell(ci) for ci, sz in SIZE_COLS.items()})
            )
    return blocks


def active_products_by_sku_prefix(sku_prefix):
    """{product_id: title} of ACTIVE products having a variant SKU starting sku_prefix.
    The '(no image)' duplicates are UNLISTED (staff stock tracking) and excluded here.
    """
    variants = client.product_variants_by_query(query_string=f"sku:{sku_prefix}*")
    return {
        v["product"]["id"]: v["product"]["title"]
        for v in variants
        if v["product"]["status"] == "ACTIVE"
    }


def product_size_options(product_id):
    variants = client.product_variants_by_product_id(product_id)
    sizes = []
    for v in variants:
        for o in v["selectedOptions"]:
            if o["name"] in ("サイズ", "Size") and o["value"] not in sizes:
                sizes.append(o["value"])
    return sizes


def generate_html(headers, rows):
    """Match the existing alvana size_table_html format (border + left align, no class)."""
    html = '\n<table border="1" style="border-collapse: collapse; text-align: left;">\n  <thead>\n    <tr>'
    for header in headers:
        html += f"\n      <th>{header}</th>"
    html += "\n    </tr>\n  </thead>\n  <tbody>"
    for row in rows:
        html += "\n    <tr>"
        for v in row:
            html += f"\n      <td>{v}</td>"
        html += "\n    </tr>"
    html += "\n  </tbody>\n</table>"
    return html


def build_size_table_html(block, lang, product_sizes=None, disclaimer=False):
    """Transpose the block into the alvana size-table HTML for the given language
    (sizes as rows, measurements as columns). Drops measurements blank/'-' for every
    size. Returns None when there is nothing to render."""
    sizes = [
        s
        for s in ("1", "2", "3", "4")
        if any(vals.get(s) not in EMPTY_VALUES for _, vals in block["meas"])
    ]
    # A single-size product (e.g. a cap) is 'F' on Shopify though the sheet lists it under ①.
    if product_sizes and len(product_sizes) == 1 and len(sizes) == 1:
        remap = {sizes[0]: product_sizes[0]}
        sizes = [product_sizes[0]]
    else:
        remap = {}

    headers, columns = ["Size"], []
    for raw, vals in block["meas"]:
        if all(vals.get(s) in EMPTY_VALUES for s in ("1", "2", "3", "4")):
            continue
        headers.append(header_for(raw, lang))
        columns.append(vals)
    if len(headers) == 1:
        return None

    table_rows = []
    for s in sizes:
        sheet_key = next((k for k, v in remap.items() if v == s), s)
        table_rows.append([s] + [vals.get(sheet_key, "") for vals in columns])
    html = generate_html(headers, table_rows)
    methods = measurement_methods([raw for raw, _ in block["meas"]])
    if methods:
        html += method_note_html(methods, lang)
    if disclaimer:
        html += f"<br><p>{DISCLAIMER_JA if lang == 'ja' else DISCLAIMER_EN}</p>"
    return html


def size_table_metafield_id(product_id):
    return client.run_query(
        'query($id: ID!) { product(id: $id) { metafield(namespace: "custom", key: "size_table_html") { id } } }',
        {"id": product_id},
    )["product"]["metafield"]["id"]


def register_en_translation(metafield_id, en_value):
    """Register the English size table as the metafield's en translation. The digest must
    match the current (ja) base value, so call this AFTER updating the base."""
    content = client.run_query(
        "query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }",
        {"id": metafield_id},
    )["translatableResource"]["translatableContent"]
    digest = next(c["digest"] for c in content if c["key"] == "value")
    res = client.run_query(
        """mutation($id: ID!, $tr: [TranslationInput!]!) {
          translationsRegister(resourceId: $id, translations: $tr) {
            userErrors { field message }
          }
        }""",
        {
            "id": metafield_id,
            "tr": [
                {
                    "locale": "en",
                    "key": "value",
                    "value": en_value,
                    "translatableContentDigest": digest,
                }
            ],
        },
    )["translationsRegister"]
    if res["userErrors"]:
        raise RuntimeError(
            f"translationsRegister failed for {metafield_id}: {res['userErrors']}"
        )


def main():
    blocks = parse_blocks()
    print(f"{len(blocks)} product blocks in sheet\n")
    updated, ignored = 0, 0
    for block in blocks:
        sku = product_sku_map.get(block["sku"], block["sku"])
        active = active_products_by_sku_prefix(sku)
        if not active:
            ignored += 1
            print(f"IGNORE {sku}: no ACTIVE product")
            continue
        if len(active) > 1:
            ignored += 1
            print(f"IGNORE {sku}: multiple ACTIVE products {list(active.values())}")
            continue
        product_id, title = next(iter(active.items()))
        disclaimer = client.to_add_disclaimer_html(title)
        sizes = product_size_options(product_id)
        ja_html = build_size_table_html(block, "ja", sizes, disclaimer)
        en_html = build_size_table_html(block, "en", sizes, disclaimer)
        if not ja_html:
            ignored += 1
            print(f"IGNORE {sku}: no size data ({title})")
            continue

        updated += 1
        print(f"\n=== {sku} -> {title}")
        print("    ja: " + " | ".join(re.findall(r"<th>(.*?)</th>", ja_html)))
        print("    en: " + " | ".join(re.findall(r"<th>(.*?)</th>", en_html)))
        if disclaimer:
            print("    + disclaimer (ja base / en translation)")
        if not DRY_RUN:
            client.update_size_table_html_metafield(
                product_id, ja_html
            )  # base = Japanese
            register_en_translation(size_table_metafield_id(product_id), en_html)

    print(f"\n{'DRY RUN — ' if DRY_RUN else ''}{updated} to update, {ignored} ignored")


if __name__ == "__main__":
    main()
