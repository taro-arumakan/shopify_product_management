"""List every leisureallstars variant with Shopify's "Charge tax" turned off.

    python -m brands.leisureallstars.list_untaxed_variants
    python -m brands.leisureallstars.list_untaxed_variants --out ~/Desktop/tax.csv

Read-only. Nothing here writes to the store.

The store is configured with tax-inclusive pricing, so ``taxable`` does not
change what a customer pays: a 27,500 yen variant charges 27,500 yen either
way. What it changes is how the order is booked -- ``taxable: false`` records
27,500 yen of net sales and zero consumption tax, where ``taxable: true``
records 25,000 + 2,500. So the products listed here understate 消費税 in every
tax report, overstate their own net sales by a factor of 1.1, and cannot
produce the per-rate tax breakdown インボイス制度 requires on a receipt.

Products created through :mod:`helpers.shopify_graphql_client.product_create`
hardcode ``taxable: True``; everything on this list predates it or was keyed in
by hand.

Two columns exist to be read before anyone flips the whole list:

* ``gift_card`` -- a gift card sale is 不課税 in Japan, with tax attaching at
  redemption instead, so a gift card SHOULD have Charge tax off. Leave it.
* ``requires_shipping`` -- false means no physical goods move, which is worth a
  second look rather than an assumption.
"""

import argparse
import csv
import datetime
import os
import unicodedata

import utils

SHOP = "leisureallstars"

#: The root productVariants connection rather than products { variants }: it
#: paginates in one dimension, so no product can silently truncate at the
#: nested page size, and it returns variants of draft and archived products too.
VARIANTS_QUERY = """
query allVariants($query_string: String!, $after: String, $first: Int!) {
  productVariants(first: $first, query: $query_string, after: $after) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      title
      sku
      price
      taxable
      inventoryItem {
        requiresShipping
      }
      product {
        id
        title
        handle
        status
        vendor
        productType
        isGiftCard
      }
    }
  }
}
"""


def all_variants(client):
    """Every variant on the store, taxable or not."""
    return client.run_paginated_query(
        query=VARIANTS_QUERY,
        variables={"query_string": ""},
        data_key="productVariants",
    )


def numeric_id(gid):
    """``gid://shopify/Product/123`` -> ``123``."""
    return gid.rsplit("/", 1)[-1]


def admin_url(product_gid):
    return f"https://admin.shopify.com/store/{SHOP}/products/{numeric_id(product_gid)}"


def to_row(variant):
    product = variant["product"]
    return {
        "vendor": product["vendor"] or "",
        "status": product["status"],
        "product_title": product["title"],
        "variant_title": variant["title"] or "",
        "sku": variant["sku"] or "",
        "price": variant["price"],
        "product_type": product["productType"] or "",
        "handle": product["handle"],
        "gift_card": product["isGiftCard"],
        "requires_shipping": (variant["inventoryItem"] or {}).get(
            "requiresShipping", True
        ),
        "admin_url": admin_url(product["id"]),
        "variant_id": variant["id"],
    }


def needs_a_decision(row):
    """True for rows that must not be swept into a blanket update."""
    return row["gift_card"] or not row["requires_shipping"]


def yen(price):
    try:
        return f"¥{float(price):,.0f}"
    except (TypeError, ValueError):
        return str(price)


def char_width(ch):
    return 2 if unicodedata.east_asian_width(ch) in "WF" else 1


def display_width(s):
    return sum(char_width(ch) for ch in s)


def fit(s, width):
    """``s`` truncated with an ellipsis and padded to ``width`` terminal columns.

    Counts an East Asian wide character as two columns. Most of this catalogue
    is Japanese, and ``str.ljust`` counts characters, which leaves the price
    column jumping around by half its width from row to row.
    """
    if display_width(s) <= width:
        return s + " " * (width - display_width(s))
    out, used = "", 0
    for ch in s:
        if used + char_width(ch) > width - 1:
            break
        out += ch
        used += char_width(ch)
    return out + "…" + " " * (width - used - 1)


def counted(rows, key):
    counts = {}
    for row in rows:
        counts[row[key]] = counts.get(row[key], 0) + 1
    return ", ".join(
        f"{name or '(none)'} {count}"
        for name, count in sorted(counts.items(), key=lambda kv: -kv[1])
    )


def report(rows, total_variants):
    """Print the list grouped by vendor then status, and the totals."""
    groups = {}
    for row in rows:
        groups.setdefault((row["vendor"], row["status"]), []).append(row)

    for (vendor, status), group in sorted(groups.items()):
        print(f"\n{vendor or '(no vendor)'}  --  {status}  ({len(group)})")
        group.sort(key=lambda r: (r["product_title"], r["variant_title"]))
        for row in group:
            name = row["product_title"]
            # "Default Title" is Shopify's placeholder on a single-variant
            # product and says nothing; a real option value does.
            if row["variant_title"] and row["variant_title"] != "Default Title":
                name = f"{name} / {row['variant_title']}"
            flags = []
            if row["gift_card"]:
                flags.append("GIFT CARD")
            if not row["requires_shipping"]:
                flags.append("no shipping")
            print(
                f"  {fit(row['sku'], 20)}  {fit(name, 46)}"
                f"  {yen(row['price']):>10}"
                + (f"  <- {', '.join(flags)}" if flags else "")
            )

    products = {row["handle"] for row in rows}
    print(
        f"\n{len(rows)} of {total_variants} variants, across {len(products)} products, "
        f"have Charge tax off."
    )
    if rows:
        print(f"  by status: {counted(rows, 'status')}")
        print(f"  by vendor: {counted(rows, 'vendor')}")

    review = [row for row in rows if needs_a_decision(row)]
    if review:
        print(
            f"\n{len(review)} of them should NOT be flipped without a decision "
            f"(see the module docstring):"
        )
        for row in review:
            why = "gift card" if row["gift_card"] else "does not require shipping"
            print(f"  {fit(row['sku'], 20)}  {row['product_title']}  -- {why}")


def write_csv(rows, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nwrote {len(rows)} rows to {path}")


def default_out():
    return os.path.expanduser(
        f"~/Downloads/{SHOP}_taxable_false_{datetime.date.today():%Y%m%d}.csv"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out",
        default=default_out(),
        help="CSV destination (default: %(default)s)",
    )
    parser.add_argument(
        "--no-csv", action="store_true", help="print the report only, write no file"
    )
    args = parser.parse_args()

    client = utils.client(SHOP)
    variants = all_variants(client)
    rows = [to_row(variant) for variant in variants if not variant["taxable"]]

    report(rows, len(variants))
    if rows and not args.no_csv:
        write_csv(rows, os.path.expanduser(args.out))


if __name__ == "__main__":
    main()
