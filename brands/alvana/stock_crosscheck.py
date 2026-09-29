"""OT-28: cross-check the owner's stock list against Shopify, and write a Japanese report.

The owner keeps stock in a spreadsheet ('alvana stock 20260521-'), column M 現在庫, keyed by
column D 'shopify SKU'. alvana is moving stock management onto Shopify, so items not sold
online are deliberately carried there too, in UNLISTED '(no image)' products -- stock that
cannot be bought is expected and is not reported as a fault.

Read-only: it writes nothing to Shopify or to either spreadsheet.

What it reports, and why each bucket is separate:

- 数量の相違      matched SKU, different quantity. The thing being looked for.
- 複数行           one SKU on several sheet rows, more than one of them non-zero. The rows
                  carry a BOX, so two boxes should sum -- but duplicate rows for the SAME
                  box also occur, and then summing double-counts. Flagged, not guessed.
- 色コード不一致   the 品番 is on Shopify but under a different colour code (sheet NT vs
                  shop NA). Reads as missing on both sides at once, so it is easy to
                  mistake for lost stock when it is the same garment twice.
- 未登録           the 品番 is nowhere on Shopify: stock for something never registered.
- シートに記載なし  Shopify holds stock the list does not mention.

Comparison is against on_hand, not available: the list is a physical count, and available
is net of unfulfilled orders. Archived products are skipped -- retiring a product by
archiving leaves its SKUs behind, and counting them would double what is on the live one.
"""

import argparse
import collections
import html
import json
import logging
import re

from brands.alvana.client import AlvanaClient

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

SHEET_ID = "1ao8v_keAlPXwx_w6rd8_sK5TSPXdsubCvkMsOcPqjGA"
TAB_ID = 876203841
FIRST_DATA_ROW = 6  # rows 1-5 are the 伝票 header block and the column titles
COL = {
    "stocktake": 0,
    "box": 1,
    "season": 2,
    "sku": 3,
    "note": 4,
    "title": 5,
    "number": 6,
    "colour": 7,
    "size": 8,
    "on_hand": 12,
}

# 20 products at a time: variants with their inventory levels cost more than the 1000-point
# ceiling on a single query at 100.
PRODUCTS_QUERY = """query($after:String){ products(first:20, after:$after){
  pageInfo{hasNextPage endCursor}
  nodes{ id title status tags
    variants(first:60){nodes{ sku inventoryQuantity
      metafield(namespace:"custom", key:"product_variant_season"){ value }
      inventoryItem{ inventoryLevels(first:2){nodes{ location{name}
        quantities(names:["on_hand","committed"]){name quantity} }} } }} } } }"""

SEASON_TAGS = {"25ss", "25aw", "25fw", "26ss", "26aw", "26fw"}


def parse_sku(sku):
    """(品番, colour code, size) or None."""
    m = re.fullmatch(r"(ALV-\d+)-([A-Z]+)-(\w+)", (sku or "").strip())
    return m.groups() if m else None


def read_sheet(client):
    worksheet = next(
        w
        for w in client.gspread_client.open_by_key(SHEET_ID).worksheets()
        if w.id == TAB_ID
    )
    per_sku, unreadable = collections.defaultdict(list), []
    for number, row in enumerate(
        worksheet.get_all_values()[FIRST_DATA_ROW - 1 :], FIRST_DATA_ROW
    ):
        row = row + [""] * (max(COL.values()) + 1)
        sku = row[COL["sku"]].strip()
        raw = row[COL["on_hand"]].strip().replace(",", "")
        if not sku:
            continue
        if re.fullmatch(r"-?\d+", raw):
            stock = int(raw)
        elif re.fullmatch(r"\(\d+\)", raw):
            stock = -int(raw[1:-1])  # the sheet shows negatives in accounting style
        elif raw in ("", "-"):
            stock = 0
        else:
            unreadable.append({"row": number, "sku": sku, "raw": row[COL["on_hand"]]})
            continue
        per_sku[sku].append(
            {
                "row": number,
                "box": row[COL["box"]].strip(),
                "season": row[COL["season"]].strip(),
                "stock": stock,
                "title": " ".join(row[COL["title"]].split()),
                "colour": row[COL["colour"]].strip(),
                "size": row[COL["size"]].strip(),
            }
        )
    return per_sku, unreadable


def shop_season(product, variant):
    """The variant's season metafield, else the product's season tag.

    The 26SS run set custom.product_variant_season on every variant it made; the 26AW run
    did not, so for those the tag is all there is.
    """
    if (variant.get("metafield") or {}).get("value"):
        return variant["metafield"]["value"].lower()
    tags = [t for t in product["tags"] if t.lower() in SEASON_TAGS]
    return f"{tags[0].lower()}（タグ）" if tags else ""


def read_shop(client):
    products, after = [], None
    while True:
        page = client.run_query(PRODUCTS_QUERY, {"after": after})["products"]
        products += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        after = page["pageInfo"]["endCursor"]
    by_sku = collections.defaultdict(list)
    for product in products:
        for variant in product["variants"]["nodes"]:
            if not variant["sku"]:
                continue
            levels = (
                (variant.get("inventoryItem") or {}).get("inventoryLevels") or {}
            ).get("nodes") or []
            quantities = {
                n["name"]: n["quantity"]
                for level in levels
                for n in level["quantities"]
            }
            by_sku[variant["sku"].strip()].append(
                {
                    "product": product["title"],
                    "status": product["status"],
                    "season": shop_season(product, variant),
                    "on_hand": quantities.get("on_hand", variant["inventoryQuantity"]),
                    "committed": quantities.get("committed", 0),
                }
            )
    return by_sku


def compare(per_sku, by_sku):
    live_codes = collections.defaultdict(dict)
    for sku, hits in by_sku.items():
        parsed = parse_sku(sku)
        if not parsed or all(h["status"] == "ARCHIVED" for h in hits):
            continue
        live = next(h for h in hits if h["status"] != "ARCHIVED")
        live_codes[parsed[0]][parsed[1]] = (
            live_codes[parsed[0]].get(parsed[1], 0) + live["on_hand"]
        )

    out = {
        "differs": [],
        "ambiguous": [],
        "mismatch": {},
        "unregistered": {},
        "not_in_sheet": [],
        "matched": 0,
        "also_archived": [],
        "negative": [],
    }
    for sku, entries in per_sku.items():
        total = sum(e["stock"] for e in entries)
        for entry in entries:
            if entry["stock"] < 0:
                out["negative"].append(
                    {
                        "sku": sku,
                        "row": entry["row"],
                        "stock": entry["stock"],
                        "title": entry["title"],
                    }
                )
        several = sum(1 for e in entries if e["stock"]) > 1
        meta = entries[0]
        hits = [h for h in by_sku.get(sku, []) if h["status"] != "ARCHIVED"]
        if not hits:
            if not total:
                continue
            parsed = parse_sku(sku)
            number = parsed[0] if parsed else sku
            bucket = out["mismatch"] if number in live_codes else out["unregistered"]
            slot = bucket.setdefault(
                number,
                {
                    "title": meta["title"],
                    "seasons": set(),
                    "sheet": {},
                    "skus": 0,
                    "units": 0,
                },
            )
            slot["seasons"].add(meta["season"])
            slot["skus"] += 1
            slot["units"] += total
            if parsed:
                slot["sheet"][parsed[1]] = slot["sheet"].get(parsed[1], 0) + total
            continue
        if len(by_sku[sku]) > len(hits):
            out["also_archived"].append(
                {
                    "sku": sku,
                    "on": [
                        (h["product"], h["status"], h["on_hand"]) for h in by_sku[sku]
                    ],
                }
            )
        hit = hits[0]
        record = {
            "sku": sku,
            "sheet": total,
            "shop": hit["on_hand"],
            "diff": hit["on_hand"] - total,
            "product": hit["product"],
            "status": hit["status"],
            "committed": hit["committed"],
            "season": meta["season"],
            "title": meta["title"],
            "colour": meta["colour"],
            "size": meta["size"],
            "rows": [e["row"] for e in entries],
            "several": several,
        }
        if hit["on_hand"] == total:
            out["matched"] += 1
        else:
            out["differs"].append(record)
        if several:
            out["ambiguous"].append(
                {
                    "sku": sku,
                    "sum": total,
                    "shop": hit["on_hand"],
                    "title": meta["title"],
                    "rows": [
                        (e["row"], e["box"], e["season"], e["stock"]) for e in entries
                    ],
                }
            )

    for sku, hits in by_sku.items():
        if sku in per_sku:
            continue
        live = next(
            (h for h in hits if h["status"] != "ARCHIVED" and h["on_hand"]), None
        )
        if live:
            out["not_in_sheet"].append(
                {
                    "sku": sku,
                    "product": live["product"],
                    "status": live["status"],
                    "shop": live["on_hand"],
                    "season": live["season"],
                }
            )
    for number, slot in out["mismatch"].items():
        slot["shop_codes"] = {
            code: units
            for code, units in live_codes[number].items()
            if code not in slot["sheet"]
        }
    return out


def suggested_pairs(slot):
    """One unmatched code on each side is a safe guess; anything else is not."""
    sheet_codes, shop_codes = list(slot["sheet"]), list(slot.get("shop_codes", {}))
    if len(sheet_codes) == 1 and len(shop_codes) == 1:
        return f"{sheet_codes[0]} → {shop_codes[0]} か"
    return ""


def render(out, unreadable):
    def esc(x):
        return html.escape(str(x))

    differs = sorted(out["differs"], key=lambda d: (-abs(d["diff"]), d["sku"]))
    sheet_units = sum(d["sheet"] for d in differs)
    shop_units = sum(d["shop"] for d in differs)
    parts = []
    parts.append(
        f"""<title>在庫数の突き合わせ結果</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Old+Mincho:wght@600&family=Noto+Sans+JP:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
 :root {{ --ground:#f4f5f2; --surface:#fff; --ink:#191d21; --muted:#5e6871; --line:#dfe2dc;
  --accent:#26384f; --accent-soft:#eaeef3; --attention:#8c5e2a; --attention-soft:#f6eee3;
  --ok:#3e6b52; --ok-soft:#e8f0ea; --minus:#8c3a3a; --minus-soft:#f6e9e9;
  --display:"Zen Old Mincho","Hiragino Mincho ProN",serif;
  --body:"Noto Sans JP","Hiragino Kaku Gothic ProN",system-ui,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace; }}
 @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --ground:#14171a; --surface:#1b1f23; --ink:#e8eae6; --muted:#9aa4ae; --line:#2c3238;
  --accent:#9bb4d0; --accent-soft:#212a35; --attention:#d6a86a; --attention-soft:#2b2318;
  --ok:#8dbc9f; --ok-soft:#1b241e; --minus:#d99a9a; --minus-soft:#2b1c1c; }} }}
 :root[data-theme="dark"] {{ --ground:#14171a; --surface:#1b1f23; --ink:#e8eae6; --muted:#9aa4ae;
  --line:#2c3238; --accent:#9bb4d0; --accent-soft:#212a35; --attention:#d6a86a;
  --attention-soft:#2b2318; --ok:#8dbc9f; --ok-soft:#1b241e; --minus:#d99a9a; --minus-soft:#2b1c1c; }}
 body {{ background:var(--ground); color:var(--ink); font-family:var(--body); font-size:15px;
  line-height:1.8; padding:0 16px; -webkit-font-smoothing:antialiased; }}
 .wrap {{ max-width:900px; margin:0 auto; padding-block:48px 72px; display:flex;
  flex-direction:column; gap:40px; }}
 p {{ margin:0; max-width:62ch; }} .lede {{ color:var(--muted); }}
 header {{ display:flex; flex-direction:column; gap:12px; }}
 .kicker {{ font-size:11px; letter-spacing:.18em; text-transform:uppercase; color:var(--muted); font-weight:500; }}
 h1 {{ font-family:var(--display); font-size:clamp(26px,6vw,36px); line-height:1.35; margin:0; font-weight:600; text-wrap:balance; }}
 .tally {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(112px,1fr)); gap:1px;
  background:var(--line); border:1px solid var(--line); border-radius:3px; overflow:hidden; }}
 .tally div {{ background:var(--surface); padding:13px 15px; }}
 .tally dt {{ font-size:12px; color:var(--muted); margin:0 0 2px; }}
 .tally dd {{ margin:0; font-family:var(--mono); font-size:20px; font-variant-numeric:tabular-nums; font-weight:500; }}
 section {{ display:flex; flex-direction:column; gap:14px; }}
 h2 {{ font-family:var(--display); font-size:19px; font-weight:600; margin:0; padding-bottom:8px; border-bottom:1px solid var(--line); }}
 h2 .count {{ font-family:var(--mono); font-size:13px; font-weight:400; color:var(--muted); margin-inline-start:10px; }}
 .note {{ font-size:13.5px; color:var(--muted); max-width:66ch; }}
 .scroll {{ overflow-x:auto; }}
 table {{ width:100%; border-collapse:collapse; font-size:13.5px; }}
 th, td {{ text-align:start; padding:7px 12px 7px 0; border-bottom:1px solid var(--line); vertical-align:top; }}
 th {{ font-size:12px; color:var(--muted); font-weight:500; white-space:nowrap; }}
 td.num {{ font-family:var(--mono); text-align:end; font-variant-numeric:tabular-nums; white-space:nowrap; padding-inline-end:16px; }}
 td.sku {{ font-family:var(--mono); font-size:12.5px; white-space:nowrap; }}
 .plus {{ color:var(--ok); }} .minus {{ color:var(--minus); }}
 .tag {{ font-size:11px; padding:1px 6px; border-radius:2px; background:var(--attention-soft); color:var(--attention); white-space:nowrap; }}
 .tag.q {{ background:var(--accent-soft); color:var(--accent); }}
 footer {{ border-top:1px solid var(--line); padding-top:18px; font-size:13px; color:var(--muted); display:flex; flex-direction:column; gap:6px; }}
</style>
<div class="wrap">
 <header>
  <span class="kicker">alvana — 在庫数の確認</span>
  <h1>在庫数の突き合わせ結果</h1>
  <p class="lede">在庫表「alvana stock 20260521-」のM列（現在庫）と、Shopifyの在庫数（実在庫）を品番ごとに突き合わせました。Shopify・在庫表のどちらも変更していません。</p>
 </header>
 <dl class="tally">
  <div><dt>一致</dt><dd>{out['matched']}</dd></div>
  <div><dt>数量の相違</dt><dd>{len(differs)}</dd></div>
  <div><dt>色コード要確認</dt><dd>{len(out['mismatch'])}</dd></div>
  <div><dt>Shopify未登録</dt><dd>{len(out['unregistered'])}</dd></div>
  <div><dt>在庫表に記載なし</dt><dd>{len(out['not_in_sheet'])}</dd></div>
 </dl>"""
    )

    parts.append(
        f"""
 <section>
  <h2>1. 数量が一致しない品番<span class="count">{len(differs)}件</span></h2>
  <p class="note">在庫表の合計 {sheet_units}点 に対し、Shopifyは {shop_units}点 です。
  差が「＋」はShopifyが多く、「−」は在庫表が多いことを示します。
  <span class="tag">複数行</span> は在庫表に同じ品番の行が複数あり、合計してよいか判断できないものです（下の項目3をご覧ください）。</p>
  <div class="scroll"><table>
   <thead><tr><th>品番</th><th>商品名</th><th>カラー / サイズ</th><th class="num">在庫表</th><th class="num">Shopify</th><th class="num">差</th><th>備考</th></tr></thead>
   <tbody>"""
    )
    for d in differs:
        cls = "plus" if d["diff"] > 0 else "minus"
        tags = ['<span class="tag">複数行</span>' if d["several"] else ""]
        if d["status"] != "ACTIVE":
            tags.append(f'<span class="tag q">{esc(d["status"])}</span>')
        if d["committed"]:
            tags.append(f'<span class="tag q">受注{d["committed"]}点</span>')
        parts.append(
            f'<tr><td class="sku">{esc(d["sku"])}</td><td>{esc(d["title"][:30])}</td>'
            f'<td>{esc(d["colour"])} / {esc(d["size"])}</td>'
            f'<td class="num">{d["sheet"]}</td><td class="num">{d["shop"]}</td>'
            f'<td class="num {cls}">{d["diff"]:+d}</td><td>{" ".join(t for t in tags if t)}</td></tr>'
        )
    parts.append("</tbody></table></div></section>")

    parts.append(
        f"""
 <section>
  <h2>2. 色コードが一致しない品番<span class="count">{len(out['mismatch'])}品番</span></h2>
  <p class="note">品番はShopifyにありますが、在庫表の色コードがShopify側に存在しません。同じ商品を別のコードで数えている可能性が高く、この場合は在庫表とShopifyの両方で「在庫が合わない」ように見えます。どちらのコードに揃えるかをご指示ください。</p>
  <div class="scroll"><table>
   <thead><tr><th>品番</th><th>商品名</th><th>在庫表のコード（点数）</th><th>Shopifyのコード（点数）</th><th>推定</th></tr></thead>
   <tbody>"""
    )
    for number, slot in sorted(
        out["mismatch"].items(), key=lambda kv: -sum(kv[1]["sheet"].values())
    ):
        sheet_s = "、".join(f"{c} ({n}点)" for c, n in slot["sheet"].items())
        shop_s = "、".join(f"{c} ({n}点)" for c, n in slot["shop_codes"].items()) or "—"
        parts.append(
            f'<tr><td class="sku">{esc(number)}</td><td>{esc(slot["title"][:28])}</td>'
            f'<td class="sku">{esc(sheet_s)}</td><td class="sku">{esc(shop_s)}</td>'
            f'<td class="sku">{esc(suggested_pairs(slot))}</td></tr>'
        )
    parts.append("</tbody></table></div></section>")

    parts.append(
        f"""
 <section>
  <h2>3. 在庫表に同じ品番の行が複数あるもの<span class="count">{len(out['ambiguous'])}品番</span></h2>
  <p class="note">BOXごとに行が分かれている場合は合計するのが正しいと思われますが、同じBOXで行が重複しているものもあり、その場合は合計すると二重計上になります。上記1の集計は単純合計で行っているため、扱いをご指示ください。</p>
  <div class="scroll"><table>
   <thead><tr><th>品番</th><th>商品名</th><th>該当行（行番号 / BOX / シーズン / 現在庫）</th><th class="num">単純合計</th><th class="num">Shopify</th></tr></thead>
   <tbody>"""
    )
    for a in sorted(out["ambiguous"], key=lambda x: -abs(x["sum"] - x["shop"])):
        rows_s = " ／ ".join(f"{r}行 {b or '—'} {s} {q}点" for r, b, s, q in a["rows"])
        parts.append(
            f'<tr><td class="sku">{esc(a["sku"])}</td><td>{esc(a["title"][:24])}</td>'
            f'<td class="note">{esc(rows_s)}</td>'
            f'<td class="num">{a["sum"]}</td><td class="num">{a["shop"]}</td></tr>'
        )
    parts.append("</tbody></table></div></section>")

    parts.append(
        f"""
 <section>
  <h2>4. Shopifyに登録がない品番<span class="count">{len(out['unregistered'])}品番</span></h2>
  <p class="note">在庫表に在庫がありますが、品番自体がShopifyにありません。Shopifyで在庫を管理するには商品登録が必要です。</p>
  <div class="scroll"><table>
   <thead><tr><th>品番</th><th>商品名</th><th>シーズン</th><th class="num">SKU数</th><th class="num">在庫数</th></tr></thead>
   <tbody>"""
    )
    for number, slot in sorted(
        out["unregistered"].items(), key=lambda kv: -kv[1]["units"]
    ):
        parts.append(
            f'<tr><td class="sku">{esc(number)}</td><td>{esc(slot["title"][:34])}</td>'
            f'<td>{esc("、".join(sorted(s for s in slot["seasons"] if s)))}</td>'
            f'<td class="num">{slot["skus"]}</td><td class="num">{slot["units"]}</td></tr>'
        )
    parts.append("</tbody></table></div></section>")

    # a colour-code mismatch shows up twice: the sheet's code in section 2 and Shopify's
    # code here, so say how much of this section that accounts for
    overlap = [
        x
        for x in out["not_in_sheet"]
        if (parse_sku(x["sku"]) or [None])[0] in out["mismatch"]
    ]
    by_product = collections.defaultdict(lambda: [0, 0])
    for x in out["not_in_sheet"]:
        slot = by_product[(x["product"], x["status"], x.get("season") or "—")]
        slot[0] += 1
        slot[1] += x["shop"]
    parts.append(
        f"""
 <section>
  <h2>5. 在庫表に記載のないShopify在庫<span class="count">{len(out['not_in_sheet'])}SKU</span></h2>
  <p class="note">Shopify側に在庫がありますが、在庫表に行がありません。9月25日に登録した26AWの商品は、在庫表の作成後に追加されたものです。シーズンは商品の登録情報から取得しています（「タグ」と付いているものは、シーズンのタグから判定したものです）。</p>
  <p class="note">このうち {len(overlap)}SKU・{sum(x["shop"] for x in overlap)}点は、上記2の色コード不一致に該当する品番です。
  同じ商品を在庫表とShopifyで別のコードで数えているため、両方の項目に現れています。
  残る {len(out["not_in_sheet"]) - len(overlap)}SKU が、在庫表に記載のない在庫です。</p>
  <div class="scroll"><table>
   <thead><tr><th>商品</th><th>シーズン</th><th>状態</th><th class="num">SKU数</th><th class="num">在庫数</th></tr></thead>
   <tbody>"""
    )
    for (product, status, season), (n, units) in sorted(
        by_product.items(), key=lambda kv: -kv[1][1]
    ):
        parts.append(
            f'<tr><td>{esc(product[:40])}</td><td class="sku">{esc(season)}</td>'
            f"<td>{esc(status)}</td>"
            f'<td class="num">{n}</td><td class="num">{units}</td></tr>'
        )
    parts.append("</tbody></table></div></section>")

    if unreadable or out["also_archived"] or out["negative"]:
        parts.append(
            '\n <section>\n  <h2>6. その他の確認事項</h2>\n  <ul class="note">'
        )
        for n in out["negative"]:
            parts.append(
                f'<li>{n["row"]}行 <span class="sku">{esc(n["sku"])}</span>'
                f'（{esc(n["title"][:24])}）の現在庫が <strong>{n["stock"]}</strong> とマイナスです。'
                f"入出荷の記録に漏れがある可能性があります</li>"
            )
        for u in unreadable:
            parts.append(
                f'<li>{u["row"]}行 <span class="sku">{esc(u["sku"])}</span> の現在庫が'
                f'「{esc(u["raw"])}」と記載されており、数量として読み取れませんでした</li>'
            )
        for a in out["also_archived"]:
            where = "、".join(f"{p}（{s}・{q}点）" for p, s, q in a["on"])
            parts.append(
                f'<li><span class="sku">{esc(a["sku"])}</span> は複数の商品に存在します（{esc(where)}）。'
                f"アーカイブ済みの商品は集計から除外しています</li>"
            )
        parts.append("</ul>\n </section>")

    parts.append(
        f"""
 <footer>
  <span>比較対象 — Shopifyの「実在庫（on hand）」と突き合わせています。受注済みで未出荷の分があると、販売可能数とは異なります。</span>
  <span>アーカイブ済みの商品は集計から除外しています。オンラインストア非公開（UNLISTED）の在庫は、店頭のみの商品として集計に含めています。</span>
 </footer>
</div>"""
    )
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", help="write the HTML report here")
    parser.add_argument("--json", help="write the raw comparison here")
    args = parser.parse_args()

    client = AlvanaClient(product_sheet_start_row=1)
    per_sku, unreadable = read_sheet(client)
    by_sku = read_shop(client)
    out = compare(per_sku, by_sku)

    print(f"sheet: {len(per_sku)} SKUs / {sum(len(v) for v in per_sku.values())} rows")
    print(
        f"  matched {out['matched']}, differs {len(out['differs'])}, "
        f"colour-code {len(out['mismatch'])}, unregistered {len(out['unregistered'])}, "
        f"only on shopify {len(out['not_in_sheet'])}, multi-row {len(out['ambiguous'])}, "
        f"unreadable {len(unreadable)}"
    )
    if args.json:
        with open(args.json, "w") as f:
            json.dump(
                {k: (sorted(v) if isinstance(v, set) else v) for k, v in out.items()},
                f,
                ensure_ascii=False,
                indent=1,
                default=lambda o: sorted(o),
            )
    if args.out:
        with open(args.out, "w") as f:
            f.write(render(out, unreadable))
        print(f"report written to {args.out}")


if __name__ == "__main__":
    main()
