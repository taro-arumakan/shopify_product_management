import logging
import utils

client = utils.client("archive-epke")
products = client.products_by_query()
promotion_products = client.products_by_collection_handle("2025-fling-promotion")
on_sale_products = client.products_by_collection_handle("on-sale")

promo_ids = [p["id"] for p in promotion_products]
on_sale_ids = [p["id"] for p in on_sale_products]
print(len(products))
print(len(promo_ids))
print(len(on_sale_ids))

for product in products:
    for variant in product["variants"]["nodes"]:
        compare_at_price = variant["compareAtPrice"] or variant["price"]
        if all((product["id"] not in promo_ids, product["id"] not in on_sale_ids)):
            price = int(compare_at_price)
            logging.info(
                f"not sale: updating price of {variant['displayName']} from {variant['price']} to {price}"
            )
        elif product["id"] in promo_ids:
            price = int(int(compare_at_price) * 0.85)
            logging.info(
                f"promo: updating price and cap of {variant['displayName']} to {price}, {compare_at_price}"
            )
        elif product["id"] in on_sale_ids:
            price = int(int(compare_at_price) * 0.8)
            logging.info(
                f"on_sale: updating price and cap of {variant['displayName']} to {price}, {compare_at_price}"
            )

        client.update_variant_attributes(
            product_id=product["id"],
            variant_id=variant["id"],
            attribute_names=["price", "compareAtPrice"],
            attribute_values=[str(price), str(compare_at_price)],
        )
