import csv
import logging
import os
from datetime import datetime
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CSVの項目
SHOPIFY_COLS = [
    "Handle",
    "Title",
    "Body (HTML)",
    "Vendor",
    "Product Category",
    "Type",
    "Tags",
    "Published",
    "Option1 Name",
    "Option1 Value",
    "Option1 Linked To",
    "Option2 Name",
    "Option2 Value",
    "Option2 Linked To",
    "Option3 Name",
    "Option3 Value",
    "Option3 Linked To",
    "Variant SKU",
    "Variant Grams",
    "Variant Inventory Tracker",
    "Variant Inventory Policy",
    "Variant Fulfillment Service",
    "Variant Price",
    "Variant Compare At Price",
    "Variant Requires Shipping",
    "Variant Taxable",
    "Unit Price Total Measure",
    "Unit Price Total Measure Unit",
    "Unit Price Base Measure",
    "Unit Price Base Measure Unit",
    "Variant Barcode",
    "Image Src",
    "Image Position",
    "Image Alt Text",
    "Gift Card",
    "SEO Title",
    "SEO Description",
    "Google Shopping / Google Product Category",
    "Google Shopping / Gender",
    "Google Shopping / Age Group",
    "Google Shopping / MPN",
    "Google Shopping / Condition",
    "Google Shopping / Custom Product",
    "Google Shopping / Custom Label 0",
    "Google Shopping / Custom Label 1",
    "Google Shopping / Custom Label 2",
    "Google Shopping / Custom Label 3",
    "Google Shopping / Custom Label 4",
    "Google: Custom Product (product.metafields.mm-google-shopping.custom_product)",
    "Complementary products (product.metafields.shopify--discovery--product_recommendation.complementary_products)",
    "Related products (product.metafields.shopify--discovery--product_recommendation.related_products)",
    "Related products settings (product.metafields.shopify--discovery--product_recommendation.related_products_display)",
    "Search product boosts (product.metafields.shopify--discovery--product_search_boost.queries)",
    "Variant Image",
    "Variant Weight Unit",
    "Variant Tax Code",
    "Cost per item",
    "Status",
]

ALL_BRANDS = [
    "gbhjapan",
    "kumej",
    "lememek",
    "rohseoul",
    "ssilkr",
    "blossomhcompany",
    "alvanas",
    "apricot-studios",
    "archive-epke",
]


def get_product_rows(product, brand_name):
    """商品をCSV行リストに変換"""
    variants = (
        (product.get("variants") or {}).get("nodes", [])
        if product.get("variants")
        else []
    )
    media = (
        (product.get("media") or {}).get("nodes", []) if product.get("media") else []
    )
    main_img_url = (
        (media[0].get("image") or {}).get("url", "")
        if media and media[0].get("image")
        else ""
    )

    opt_names = (
        [o.get("name", "") for o in (variants[0].get("selectedOptions") or [])]
        if variants and variants[0].get("selectedOptions")
        else []
    ) + [""] * 3
    rows = []
    for idx, v in enumerate(variants):
        opts = [o.get("value", "") for o in (v.get("selectedOptions") or [])] + [""] * 3
        v_img = (v.get("image") or {}).get("url") if v.get("image") else main_img_url

        rows.append(
            {
                "Handle": product.get("handle", ""),
                "Title": product.get("title", ""),
                "Body (HTML)": product.get("descriptionHtml", "") or "",
                "Vendor": brand_name.upper(),
                "Product Category": "",
                "Type": "",
                "Tags": ",".join(product.get("tags", [])),
                "Published": "TRUE" if product.get("status") == "ACTIVE" else "FALSE",
                "Option1 Name": opt_names[0],
                "Option1 Value": opts[0],
                "Option1 Linked To": "",
                "Option2 Name": opt_names[1],
                "Option2 Value": opts[1],
                "Option2 Linked To": "",
                "Option3 Name": opt_names[2],
                "Option3 Value": opts[2],
                "Option3 Linked To": "",
                "Variant SKU": v.get("sku", ""),
                "Variant Grams": "",
                "Variant Inventory Tracker": "shopify",
                "Variant Inventory Policy": "deny",
                "Variant Fulfillment Service": "manual",
                "Variant Price": v.get("price", ""),
                "Variant Compare At Price": v.get("compareAtPrice", "") or "",
                "Variant Requires Shipping": "TRUE",
                "Variant Taxable": "TRUE",
                "Variant Barcode": "",
                "Image Src": main_img_url if idx == 0 else "",
                "Image Position": "1" if idx == 0 else "",
                "Image Alt Text": product.get("title", "") if idx == 0 else "",
                "Gift Card": "FALSE",
                "Variant Image": v_img,
                "Variant Weight Unit": "kg",
                "Status": "active" if product.get("status") == "ACTIVE" else "draft",
                **{
                    k: ""
                    for k in SHOPIFY_COLS
                    if k
                    not in [
                        "Handle",
                        "Title",
                        "Body (HTML)",
                        "Vendor",
                        "Product Category",
                        "Type",
                        "Tags",
                        "Published",
                        "Option1 Name",
                        "Option1 Value",
                        "Option1 Linked To",
                        "Option2 Name",
                        "Option2 Value",
                        "Option2 Linked To",
                        "Option3 Name",
                        "Option3 Value",
                        "Option3 Linked To",
                        "Variant SKU",
                        "Variant Inventory Tracker",
                        "Variant Inventory Policy",
                        "Variant Fulfillment Service",
                        "Variant Price",
                        "Variant Compare At Price",
                        "Variant Requires Shipping",
                        "Variant Taxable",
                        "Image Src",
                        "Image Position",
                        "Image Alt Text",
                        "Gift Card",
                        "Variant Image",
                        "Variant Weight Unit",
                        "Status",
                    ]
                },
            }
        )
    return rows


def process(brand, folder_id):
    logger.info(f"Processing {brand}...")
    client = utils.client(brand)
    products = client.products_by_query(additional_fields=["descriptionHtml"])

    filepath = os.path.join(
        "/tmp/exports", f"{brand}_products_{datetime.now():%Y%m%d}.csv"
    )

    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SHOPIFY_COLS, extrasaction="ignore")
        writer.writeheader()
        for p in products:
            writer.writerows(get_product_rows(p, brand))

    logger.info(f"Saved: {filepath}")
    if folder_id:
        client.upload_to_drive(filepath, folder_id)


def process_brands(folder_id=None):
    os.makedirs("/tmp/exports", exist_ok=True)
    results = {}
    for brand in ALL_BRANDS:
        try:
            process(brand, folder_id)
            results[brand] = "Success"
        except Exception as e:
            logger.error(f"Error {brand}: {e}")
            results[brand] = str(e)
    return results


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    folder_id = os.environ.get("PRODUCT_EXPORT_DRIVE_FOLDER_ID")
    process_brands(folder_id=folder_id)
