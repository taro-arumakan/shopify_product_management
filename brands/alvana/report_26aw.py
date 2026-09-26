"""OT-28: turn the 26AW run into a Japanese summary for the shop owner and the staff
member who checks the products.

The run prints its plan before it executes anything, so that plan is the record of what
was done. This reads it back, resolves each product to its admin page, and writes the
report to stdout (and to --out, if given).

    python brands/alvana/report_26aw.py run_main.log --out report.md
"""

import argparse
import collections
import datetime
import logging
import re

from brands.alvana.client import AlvanaClient
from brands.alvana.product_create_26aw import (
    APPEND_IMAGES,
    COLOUR_ALIASES,
    CREATE_LIVE,
    CREATE_TWIN,
    FILTER_COLOUR_ALIASES,
    HELD,
    NOTHING,
    PROMOTE,
)

logging.basicConfig(level=logging.ERROR)

ACTIONS = [CREATE_LIVE, CREATE_TWIN, PROMOTE, APPEND_IMAGES, NOTHING, HELD]
PLAN_LINE = re.compile(
    r"^ {2}(?P<colour>.+?)\s{2,}"
    r"(?P<action>" + "|".join(re.escape(a) for a in ACTIONS) + r")\s+"
    r"(?P<skus>\S+)"
    r"(?:\s+(?P<images>\d+) image\(s\))?"
    r"\s*(?P<detail>.*?)\s*$"
)
QUOTED = re.compile(r"'([^']+)'")
TODAY = f"{datetime.date.today():%Y%m%d}"

# Held back for the brand to confirm; the plan's reason is in English, the report is not.
HELD_REASONS = {
    "1960s JP JACKET": "シートのDARK GRAYは`ALV-00159-GY-*`ですが、公開中の26SS商品は"
    "`ALV-00159-DGY-*`です。同じカラー名で品番が異なるため、確認後に対応します",
}

# Colourways worth a second look when the next drop is prepared: they exist on the shop
# but the 26AW sheet does not list them.
DROP_CANDIDATES = [
    (
        "ALV-90102-BL-0",
        "BHARAT DENIM SKATE PANTS",
        "サイズ0。在庫0で、26AWのシートには記載なし",
    ),
    (
        "ALV-90102-BL-0 / ALV-90102-BL-1",
        "BHARAT DENIM SKATE PANTS",
        "この2点のみ絞り込み用カラーが未設定（2024年登録分）。他のBLUEは`BLUE`が設定済み",
    ),
]

# The three BHARAT DENIM SKATE PANTS products merged into one, handled separately from
# the sheet-driven run.
CONSOLIDATION = {
    "survivor": "BHARAT DENIM SKATE PANTS",
    "was": "BHARAT DENIM SKATE PANTS BLUE",
    "merged": [
        (
            "BLACK",
            "BHARAT DENIM SKATE PANTS BLACK",
            "在庫（2:3点 / 3:2点 / 4:1点）と画像5点を引き継ぎ",
        ),
        (
            "INK BLACK",
            "BHARAT DENIM SKATE PANTS (no image)",
            "シートの画像5点を登録、在庫0",
        ),
    ],
    "archived": [
        "BHARAT DENIM SKATE PANTS BLACK",
        "BHARAT DENIM SKATE PANTS (no image)",
    ],
}


def parse_plan(path):
    """[(sheet title, colour, action, skus, image count, detail)] from the run log."""
    rows, title = [], None
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("--- totals"):
                break
            if not line.strip() or line.startswith(("INFO:", "WARNING:", "/Users/")):
                continue
            if not line.startswith("  "):
                title = line.strip()
                continue
            if match := PLAN_LINE.match(line):
                rows.append(
                    (
                        title,
                        match["colour"].strip(),
                        match["action"],
                        match["skus"],
                        int(match["images"] or 0),
                        match["detail"],
                    )
                )
    return rows


def shop_title_of(row):
    """The product the colourway ends up on."""
    title, _, action, _, _, detail = row
    quoted = QUOTED.search(detail)
    if action == CREATE_TWIN:
        return f"{title} (no image)"
    if action == CREATE_LIVE:
        return title
    if action == PROMOTE and quoted:
        return quoted.group(1).replace(" (no image)", "")
    return quoted.group(1) if quoted else title


def shop_state(client):
    query = """query($after:String){ products(first:100, after:$after){
      pageInfo{hasNextPage endCursor}
      nodes{ id title status
        media(first:100){nodes{... on MediaImage{ image{ url } }}} } } }"""
    products, after = [], None
    while True:
        page = client.run_query(query, {"after": after})["products"]
        products += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        after = page["pageInfo"]["endCursor"]
    return {p["title"]: p for p in products}


def admin_links(client, by_title, titles):
    links = {}
    for title in titles:
        if product := by_title.get(title):
            links[title] = (
                f"https://admin.shopify.com/store/{client.shop_name}"
                f"/products/{product['id'].rsplit('/', 1)[-1]}",
                product["status"],
            )
    return links


def images_added_today(by_title, shop_title, sku):
    """How many images this colourway actually gained, counted on the product itself.

    The plan's count is what the drive folder held that the product did not; a promotion
    uploads the whole folder, so the two differ. What the product now carries is the
    honest number for a report someone will check against the screen.
    """
    product = by_title.get(shop_title)
    if not product:
        return 0
    names = [
        m["image"]["url"].split("/")[-1].split("?")[0]
        for m in product["media"]["nodes"]
        if m.get("image")
    ]
    return sum(
        1
        for name in names
        if sku in name and (TODAY in name or name.startswith("append_"))
    )


def bullet(title, links, suffix=""):
    url, status = links.get(title, (None, None))
    label = f"[{title}]({url})" if url else title
    return f"- {label}{suffix}"


def render(rows, links, by_title):
    by_action = collections.defaultdict(list)
    for row in rows:
        by_action[row[2]].append(row)

    out = ["# alvana 26AW 商品登録 作業報告", ""]
    out += [
        "商品マスタ「26AW Product Master」をもとに登録作業を行いました。",
        "既存商品の在庫数は変更していません。新規登録分はすべて在庫0で登録しています"
        "（商品を統合した分のみ、統合元の在庫をそのまま引き継いでいます）。",
        "シートのT列（変更情報）に、今回登録・更新した内容を記載しました。",
        "",
    ]

    out += ["## 新規登録した商品", ""]
    grouped = collections.defaultdict(list)
    for row in by_action[CREATE_LIVE]:
        grouped[shop_title_of(row)].append(row[1])
    for title, colours in grouped.items():
        out.append(bullet(title, links, f" — {'、'.join(colours)}（公開）"))
    out.append("")

    out += [
        "## 画像未入稿のため非公開で登録した商品",
        "",
        "画像が届き次第、公開商品へ移動します。",
        "",
    ]
    grouped = collections.defaultdict(list)
    for row in by_action[CREATE_TWIN]:
        grouped[shop_title_of(row)].append(row[1])
    for title, colours in grouped.items():
        out.append(bullet(title, links, f" — {'、'.join(colours)}（非公開）"))
    out.append("")

    out += [
        "## 公開商品へ移動したカラー",
        "",
        "画像が入稿されたため、非公開商品から公開商品へ移動しました。在庫は引き継いでいます。",
        "",
    ]
    for row in by_action[PROMOTE]:
        shop_title = shop_title_of(row)
        count = images_added_today(by_title, shop_title, row[3].split("..")[0])
        out.append(bullet(shop_title, links, f" — {row[1]}（画像{count}点）"))
    out.append("")

    out += [
        "## 画像を追加した商品（ご確認をお願いします）",
        "",
        "既存の商品ページに、新しい画像を末尾へ追加しました。並び順のご確認をお願いします。",
        "",
    ]
    grouped = collections.defaultdict(list)
    for row in by_action[APPEND_IMAGES]:
        shop_title = shop_title_of(row)
        count = images_added_today(by_title, shop_title, row[3].split("..")[0])
        grouped[shop_title].append(f"{row[1]}に{count}点")
    for title, added in grouped.items():
        out.append(bullet(title, links, f" — {'、'.join(added)}追加"))
    out.append("")

    out += [
        "## カラー表記の統一",
        "",
        "シートの表記を、ショップ既存の表記に合わせて登録しました。今後も同様に統一します。",
        "",
    ]
    for sheet_value, shop_value in COLOUR_ALIASES.items():
        out.append(f"- カラー名: `{sheet_value}` → `{shop_value}`")
    for sheet_value, shop_value in FILTER_COLOUR_ALIASES.items():
        out.append(f"- 絞り込み用カラー: `{sheet_value}` → `{shop_value}`")
    out += [
        "",
        "※ 絞り込み用カラーは、お客様が色で商品を絞り込むための項目です。"
        "`TOP GRAY` は既存の選択肢になく、そのままでは絞り込みに表示されないため `GRAY` としています。"
        "商品ページ上のカラー名は `TOP GRAY` のままです。",
        "",
    ]

    out += [
        "## 商品の統合",
        "",
        f"同じ商品が3つに分かれて登録されていたため、{CONSOLIDATION['survivor']}に統合しました。",
        "旧商品のURLは統合後の商品へ転送されるため、お客様のブックマークや外部リンクはそのまま使えます。",
        "",
    ]
    out.append(
        bullet(
            CONSOLIDATION["survivor"],
            links,
            f"（旧「{CONSOLIDATION['was']}」。カラー名を商品名から外しました）",
        )
    )
    for colour, source, note in CONSOLIDATION["merged"]:
        out.append(f"    - {colour}：「{source}」より統合。{note}")
    out.append(
        f"- 統合元の2商品はアーカイブしました（削除はしていません）："
        f"{'、'.join(CONSOLIDATION['archived'])}"
    )
    out.append("")

    out += ["## 今後ご検討いただきたい点", ""]
    for sku, title, note in DROP_CANDIDATES:
        out.append(bullet(title, links, f" — `{sku}`：{note}"))
    out.append("")

    held = [row for row in by_action[HELD] if row[0] != CONSOLIDATION["survivor"]]
    if held:
        out += ["## 確認待ちのため未処理の商品", ""]
        for title in dict.fromkeys(row[0] for row in held):
            out.append(f"- {title} — {HELD_REASONS.get(title, '確認中')}")
        out.append("")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log", help="stdout of the 26AW run, with its plan")
    parser.add_argument("--out")
    args = parser.parse_args()

    rows = parse_plan(args.log)
    rows = [row for row in rows if row[2] != NOTHING]
    client = AlvanaClient(product_sheet_start_row=1)
    by_title = shop_state(client)
    links = admin_links(
        client,
        by_title,
        {shop_title_of(row) for row in rows}
        | {title for _, title, _ in DROP_CANDIDATES}
        | {CONSOLIDATION["survivor"]},
    )
    report = render(rows, links, by_title)
    print(report)
    if args.out:
        with open(args.out, "w") as f:
            f.write(report)


if __name__ == "__main__":
    main()
