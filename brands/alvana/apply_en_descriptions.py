"""Apply the reviewed English product descriptions (from the 'EN Desc Drafts' tab):
- normalize the base (ja) description's 原産国 value to 'Japan' (JAPAN -> Japan),
- register the en body_html translation built from the reviewed EN prose + a translated
  spec table (素材->Material, 原産国->Country of Origin: Japan, 品番->Product No.).

The en is derived from the current base HTML by targeted replacement, so structure is
preserved. Run after base origin normalization (digest must be current)."""

import re
import utils

client = utils.client("alvana")

REVIEW_SHEET_ID = "1l4RmXLPSeuLu9b2HY7oelKEyiPfaf1Wi7pFdb5rA614"
REVIEW_TAB = "EN Desc Drafts"
DRY_RUN = True


def normalize_origin(html):
    """JAPAN (any case) -> Japan in the 原産国 row of the base HTML."""

    def repl(m):
        val = m.group(2).strip()
        return (
            m.group(1)
            + ("Japan" if val.lower() == "japan" else m.group(2))
            + m.group(3)
        )

    return re.sub(
        r"(<th>\s*原産国\s*</th>\s*<td>)(.*?)(</td>)", repl, html, count=1, flags=re.S
    )


def build_en(base, en_prose, en_material):
    html = base
    if en_prose:
        html = re.sub(
            r"<p>.*?</p>", lambda m: f"<p>{en_prose}</p>", html, count=1, flags=re.S
        )
    html = re.sub(r"<th>\s*素材\s*</th>", "<th>Material</th>", html)
    html = re.sub(r"<th>\s*原産国\s*</th>", "<th>Country of Origin</th>", html)
    html = re.sub(r"<th>\s*品番\s*</th>", "<th>Product No.</th>", html)
    html = re.sub(
        r"(<th>\s*Material\s*</th>\s*<td>).*?(</td>)",
        lambda m: m.group(1) + en_material + m.group(2),
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(
        r"(<th>\s*Country of Origin\s*</th>\s*<td>).*?(</td>)",
        lambda m: m.group(1) + "Japan" + m.group(2),
        html,
        count=1,
        flags=re.S,
    )
    return html


def register_en_body_html(product_id, en_html):
    content = client.run_query(
        "query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }",
        {"id": product_id},
    )["translatableResource"]["translatableContent"]
    digest = next(c["digest"] for c in content if c["key"] == "body_html")
    res = client.run_query(
        """mutation($id: ID!, $tr: [TranslationInput!]!) {
          translationsRegister(resourceId: $id, translations: $tr) {
            userErrors { field message }
          }
        }""",
        {
            "id": product_id,
            "tr": [
                {
                    "locale": "en",
                    "key": "body_html",
                    "value": en_html,
                    "translatableContentDigest": digest,
                }
            ],
        },
    )["translationsRegister"]
    if res["userErrors"]:
        raise RuntimeError(
            f"register body_html failed for {product_id}: {res['userErrors']}"
        )


def main():
    ws = client.gspread_client.open_by_key(REVIEW_SHEET_ID).worksheet(REVIEW_TAB)
    sheet = {
        r[0]: {"en_prose": r[4], "en_material": r[6]} for r in ws.get_all_values()[1:]
    }
    by_title = {
        p["title"]: p
        for p in client.products_by_query("")
        if p["status"] == "ACTIVE" and "(no image)" not in p["title"]
    }
    dq = "query($id: ID!) { product(id: $id) { descriptionHtml } }"
    mut = """mutation($id: ID!, $html: String!) {
      productUpdate(input: {id: $id, descriptionHtml: $html}) { userErrors { field message } }
    }"""

    origin_fixed = registered = missing = 0
    samples = []
    for title, d in sheet.items():
        p = by_title.get(title)
        if not p:
            missing += 1
            print(f"SKIP (no active product): {title}")
            continue
        base = client.run_query(dq, {"id": p["id"]})["product"]["descriptionHtml"] or ""
        base_norm = normalize_origin(base)
        en_html = build_en(base_norm, d["en_prose"].strip(), d["en_material"].strip())
        if len(samples) < 2:
            samples.append((title, en_html))
        if not DRY_RUN:
            if base_norm != base:
                r = client.run_query(mut, {"id": p["id"], "html": base_norm})[
                    "productUpdate"
                ]
                if r["userErrors"]:
                    raise RuntimeError(f"base update failed {title}: {r['userErrors']}")
            register_en_body_html(p["id"], en_html)
        origin_fixed += base_norm != base
        registered += 1

    print(
        f"\n{'DRY RUN — ' if DRY_RUN else ''}{registered} en descriptions, {origin_fixed} base origins normalized, {missing} missing"
    )
    for title, html in samples:
        print(f"\n===== {title}\n{html}")


if __name__ == "__main__":
    main()
