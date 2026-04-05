import datetime
import logging
import os
import dotenv
import utils

logging.basicConfig(level=logging.INFO)


def get_date_metafield_value(metafields, key):
    if metafield := [m for m in metafields if m["key"] == key]:
        return datetime.datetime.fromisoformat(metafield[0]["value"]).date()


def to_num_id(gid: str):
    return gid.rsplit("/", 1)[-1]


def check(brand, email_recipients):
    client = utils.client(brand.lower())
    products = client.products_by_query("status:'ACTIVE'")

    products_outdated = []
    variants_outdated = []

    admin_url_base = f"https://admin.shopify.com/store/{client.shop_name}/products"

    for product in products:
        if expected_shipping_date := get_date_metafield_value(
            product["metafields"]["nodes"], "expected_shipping_date"
        ):
            if expected_shipping_date <= datetime.date.today():
                products_outdated.append(
                    (
                        expected_shipping_date,
                        product["title"],
                        f"{admin_url_base}/{to_num_id(product['id'])}",
                    )
                )
        for variant in product["variants"]["nodes"]:
            if variant_expected_shipping_date := get_date_metafield_value(
                variant["metafields"]["nodes"], "variant_expected_shipping_date"
            ):
                if variant_expected_shipping_date <= datetime.date.today():
                    variants_outdated.append(
                        (
                            variant_expected_shipping_date,
                            variant["displayName"],
                            f"{admin_url_base}/{to_num_id(product['id'])}/variants/{to_num_id(variant['id'])}",
                        )
                    )

    body = ""
    if products_outdated:
        body += "<h3>products with outdated expected shpping date</h3>\n"
        for d, t, url in sorted(products_outdated, key=lambda x: x[0]):
            body += f'<p>{d} <a href="{url}">{t}</a></p>\n'
        body += "<br>\n"

    if variants_outdated:
        body += "<h3>variants with outdated expected shpping date</h3>\n"
        for d, t, url in sorted(variants_outdated, key=lambda x: x[0]):
            body += f'<p>{d} <a href="{url}">{t}</a></p>\n'

    if body:
        body = f"""
        <html>
          <body>
            {body}
          </body>
        </html>
        """
        print(body)
        client.send_email(
            f"{brand} - expected shipping date in the past",
            body,
            email_recipients,
            subtype="html",
        )


def main():
    assert dotenv.load_dotenv(override=True)
    brands = ["KUME", "GBH", "BLOSSOM", "LEMEME"]
    for brand in brands:
        logging.info(f"Checking {brand}...")
        check(brand, email_recipients=["taro@sniarti.fi"])
        # check(brand, email_recipients=os.environ[f"NOTIFYEES_{brand}"].split(","))


if __name__ == "__main__":
    main()
