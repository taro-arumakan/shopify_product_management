import logging
import pprint
import utils

logging.basicConfig(level=logging.INFO)

from brands.dev.client import dev_client


def variants_to_options_dict(variants):
    return [
        dict(
            option_values={
                so["name"]: so["value"] for so in variant["selectedOptions"]
            },
            price=variant["compareAtPrice"],
            sku=variant["sku"],
            stock=variant["inventoryQuantity"],
        )
        for variant in variants
    ]


def test_merge_products_as_variants():
    client = dev_client(utils.client("LEMEME"))
    product_title = "Elene Sheer Layered Skirt"
    products = client.products_by_query(f"title:{product_title}*")
    client.merge_products_as_variants(
        products=products, new_product_title=product_title
    )


def clone():
    clientfrom = utils.client("lememe")
    clientto = utils.client("dev")
    location_name = "Shop location"

    handles = [
        "archived-20260420-elene-sheer-layered-skirt-white",
        "archived-20260420-elene-sheer-layered-skirt-black",
    ]
    for handle in handles:
        product = clientfrom.product_by_handle(
            handle,
            additional_fields=["descriptionHtml", "vendor"],
            filter_archived=False,
        )

        """ client.process_product_input """
        res = clientto.product_create(
            title=product["title"],
            handle=product["handle"],
            description_html=product["descriptionHtml"],
            vendor=product["vendor"],
            tags=product["tags"],
            option_dicts=variants_to_options_dict(product["variants"]["nodes"]),
        )
        pprint.pprint(res)
        product_id = res["id"]
        skus, prices, compare_at_prices = zip(
            *[
                (v["sku"], v["price"], v["compareAtPrice"])
                for v in product["variants"]["nodes"]
            ]
        )
        clientto.update_variant_prices_by_skus(
            product_id=product_id,
            skus=skus,
            prices=prices,
            compare_at_prices=compare_at_prices,
        )
        for sku in skus:
            clientto.enable_and_activate_inventory_by_sku(sku, [location_name])
        """ #TODO [CEC-342] clone images client.product_product_images """

        """ client.update_stocks """
        location_id = clientto.location_id_by_name(location_name)
        sku_stock_map = {
            v["sku"]: v["inventoryQuantity"] for v in product["variants"]["nodes"]
        }
        for sku, stock in sku_stock_map.items():
            clientto.set_inventory_quantity_by_sku_and_location_id(
                sku, location_id, stock
            )

        """ client.publish_products """
        clientto.activate_and_publish_by_product_id(
            product_id=product_id, scheduled_time=None
        )


if __name__ == "__main__":
    test_merge_products_as_variants()
