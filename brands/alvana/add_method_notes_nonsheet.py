"""Append the CB/NP measurement-method note to size tables of ACTIVE products that are
NOT in the 26 S/S sheet (their tables aren't rebuilt by update_size_field, so the note is
inserted directly). Detects the method from the product's own base headers, inserts the
note right after </table> on both the ja base and the en translation. Idempotent.

The 26 S/S sheet products get their method note from update_size_field.py instead."""

import re
import utils
import brands.alvana.update_size_field as u

client = utils.client("alvana")

DRY_RUN = True


def sheet_product_titles():
    titles = set()
    for b in u.parse_blocks():
        active = u.active_products_by_sku_prefix(
            u.product_sku_map.get(b["sku"], b["sku"])
        )
        titles.update(active.values())
    return titles


def insert_note(html, note):
    if not note or note in html:
        return html
    return html.replace("</table>", "</table>" + note, 1)


def en_value(metafield_id):
    tr = client.run_query(
        'query($id: ID!) { translatableResource(resourceId: $id) { translations(locale: "en") { key value } } }',
        {"id": metafield_id},
    )["translatableResource"]["translations"]
    return next((t["value"] for t in tr if t["key"] == "value"), None)


def main():
    sheet_titles = sheet_product_titles()
    done = []
    for p in client.products_by_query(""):
        if (
            p["status"] != "ACTIVE"
            or "(no image)" in p["title"]
            or p["title"] in sheet_titles
        ):
            continue
        mfs = [
            m
            for m in p["metafields"]["nodes"]
            if m["key"] == "size_table_html" and m["value"]
        ]
        if not mfs:
            continue
        base = mfs[0]["value"]
        methods = u.measurement_methods(re.findall(r"<th>(.*?)</th>", base))
        if not methods:
            continue
        new_base = insert_note(base, u.method_note_html(methods, "ja"))
        cur_en = en_value(mfs[0]["id"])
        new_en = (
            insert_note(cur_en, u.method_note_html(methods, "en")) if cur_en else cur_en
        )
        done.append((p["title"], sorted(methods)))
        print(
            f"{p['title']}: {sorted(methods)} | base+note={new_base != base} | en+note={new_en != cur_en}"
        )
        if not DRY_RUN:
            if new_base != base:
                client.update_size_table_html_metafield(p["id"], new_base)
            if new_en and new_en != cur_en:
                u.register_en_translation(u.size_table_metafield_id(p["id"]), new_en)
    print(
        f"\n{'DRY RUN — ' if DRY_RUN else ''}{len(done)} non-sheet products with method note"
    )


if __name__ == "__main__":
    main()
