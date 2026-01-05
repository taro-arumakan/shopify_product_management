import datetime
import utils


def get_date_metafield_value(metafields, key):
    if metafield := [m for m in metafields if m["key"] == key]:
        return datetime.datetime.fromisoformat(metafield[0]["value"]).date()


def check(brand, email_recipients):
    client = utils.client(brand.lower())
    products = client.products_by_query("status:'ACTIVE'")

    products_outdated = []
    variants_outdated = []

    for product in products:
        if expected_shipping_date := get_date_metafield_value(
            product["metafields"]["nodes"], "expected_shipping_date"
        ):
            if expected_shipping_date <= datetime.date.today():
                products_outdated.append((expected_shipping_date, product["title"]))
        for variant in product["variants"]["nodes"]:
            if variant_expected_shipping_date := get_date_metafield_value(
                variant["metafields"]["nodes"], "variant_expected_shipping_date"
            ):
                if variant_expected_shipping_date <= datetime.date.today():
                    variants_outdated.append(
                        (variant_expected_shipping_date, variant["displayName"])
                    )

    body = ""
    if products_outdated:
        body += "products with outdated expected shpping date\n"
        for d, t in sorted(products_outdated, key=lambda x: x[0]):
            body += f"{d}\t{t}\n"
        body += "\n"

    if variants_outdated:
        body += "variants with outdated expected shpping date\n"
        for d, t in sorted(variants_outdated, key=lambda x: x[0]):
            body += f"{d}\t{t}\n"

    if body:
        print(body)
        client.send_email(
            f"{brand} - expected shipping date in the past",
            body,
            email_recipients,
        )


def main():
    brands = ["KUME", "GBH"]
    recipients_by_brand = {
        "KUME": ["marina6529@kume-studio.co.kr", "taro@sniarti.fi"],
        "GBH": ["gbh338@jaebum.com", "taro@sniarti.fi"],
    }
    for brand in brands:
        check(brand, recipients_by_brand[brand])


if __name__ == "__main__":
    main()
