"""Read-only QA of alvana en-eu localization. For every ACTIVE (non '(no image)') product
checks the en title, en description (body_html) and en size_table_html — present? outdated?
any Japanese left? — plus base 原産国 normalization. Prints only anomalies."""

import re
import utils

client = utils.client("alvana")

JA = re.compile(r"[぀-ヿ一-龯]")


def en_for(resource_id):
    tr = client.run_query(
        'query($id: ID!) { translatableResource(resourceId: $id) { translations(locale: "en") { key value outdated } } }',
        {"id": resource_id},
    )["translatableResource"]["translations"]
    return {t["key"]: t for t in tr}


def main():
    products = [
        p
        for p in client.products_by_query("")
        if p["status"] == "ACTIVE" and "(no image)" not in p["title"]
    ]
    # bulk product-level translations (title, body_html)
    prod_en, after = {}, None
    while True:
        r = client.run_query(
            'query($after: String) { translatableResources(first: 100, resourceType: PRODUCT, after: $after) { pageInfo { hasNextPage endCursor } nodes { resourceId translatableContent { key value } translations(locale: "en") { key value outdated } } } }',
            {"after": after},
        )["translatableResources"]
        for n in r["nodes"]:
            prod_en[n["resourceId"]] = n
        if not r["pageInfo"]["hasNextPage"]:
            break
        after = r["pageInfo"]["endCursor"]

    issues = []
    for p in products:
        node = prod_en.get(p["id"])
        base = (
            {c["key"]: (c["value"] or "") for c in node["translatableContent"]}
            if node
            else {}
        )
        en = {t["key"]: t for t in node["translations"]} if node else {}

        # en title (only required when base title has Japanese)
        if JA.search(base.get("title", "")) and not en.get("title", {}).get("value"):
            issues.append((p["title"], "en TITLE missing (base has Japanese)"))

        # en description
        if base.get("body_html", "").strip():
            b = en.get("body_html")
            if not b or not b["value"]:
                issues.append((p["title"], "en DESCRIPTION missing"))
            else:
                if b["outdated"]:
                    issues.append((p["title"], "en DESCRIPTION outdated"))
                if JA.search(b["value"]):
                    issues.append((p["title"], "en DESCRIPTION contains Japanese"))
        # base origin not normalized
        if re.search(
            r"原産国\s*</th>\s*<td>\s*JAPAN\s*</td>", base.get("body_html", "")
        ):
            issues.append((p["title"], "base 原産国 still 'JAPAN' (not normalized)"))

        # en size table
        mfs = [
            m
            for m in p["metafields"]["nodes"]
            if m["key"] == "size_table_html" and m["value"]
        ]
        if mfs:
            ste = en_for(mfs[0]["id"]).get("value")
            if not ste or not ste["value"]:
                issues.append((p["title"], "en SIZE TABLE missing"))
            else:
                if ste["outdated"]:
                    issues.append((p["title"], "en SIZE TABLE outdated"))
                if JA.search(ste["value"]):
                    issues.append((p["title"], "en SIZE TABLE contains Japanese"))

    print(f"checked {len(products)} active products")
    if not issues:
        print("ALL CLEAN — no en anomalies")
    else:
        print(f"{len(issues)} issue(s):")
        for title, msg in issues:
            print(f"  - {title}: {msg}")


if __name__ == "__main__":
    main()
