import json
import logging
from helpers.shopify_graphql_client.client import ShopifyGraphqlClient

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)


def product_variants_to_products(shop_name, access_token, product_title):
    return ShopifyGraphqlClient(shop_name, access_token).product_variants_to_products(product_title)

def update_product_attribute(shop_name, access_token, product_id, attribute_name, attribute_value):
    return ShopifyGraphqlClient(shop_name, access_token).update_product_attribute(product_id, attribute_name, attribute_value)

def update_product_tags(shop_name, access_token, product_id, tags):
    return update_product_attribute(shop_name, access_token, product_id, 'tags', tags)

def update_product_description(shop_name, access_token, product_id, desc):
    return update_product_attribute(shop_name, access_token, product_id, 'descriptionHtml', desc)

def update_product_handle(shop_name, access_token, product_id, handle):
    return update_product_attribute(shop_name, access_token, product_id, 'handle', handle)

def upload_and_assign_description_images_to_shopify(shop_name, access_token, product_id, local_paths, dummy_product_id, shopify_url_prefix):
    return ShopifyGraphqlClient(shop_name, access_token).upload_and_assign_description_images_to_shopify(product_id, local_paths, dummy_product_id, shopify_url_prefix)

def file_id_by_file_name(shop_name, access_token, file_name):
    return ShopifyGraphqlClient(shop_name, access_token).file_id_by_file_name(file_name)

def replace_image_files(shop_name, access_token, local_paths):
    return ShopifyGraphqlClient(shop_name, access_token).replace_image_files(local_paths)

def update_product_metafield(shop_name, access_token, product_id, metafield_namespace, metafield_key, value):
    return ShopifyGraphqlClient(shop_name, access_token).update_product_metafield(product_id, metafield_namespace, metafield_key, value)

def update_variation_value_metafield(shop_name, access_token, product_id, variation_value):
    return update_product_metafield(shop_name, access_token, product_id, 'custom', 'variation_value', variation_value)

def update_variation_products_metafield(shop_name, access_token, product_id, variation_product_ids):
    return update_product_metafield(shop_name, access_token, product_id, 'custom', 'variation_products', json.dumps(variation_product_ids))

def update_product_description_metafield(shop_name, access_token, product_id, desc):
    return update_product_metafield(shop_name, access_token, product_id, 'custom', 'product_description', json.dumps(desc))

def update_size_table_html_metafield(shop_name, access_token, product_id, html_text):
    return update_product_metafield(shop_name, access_token, product_id, 'custom', 'size_table_html', html_text)

def metafield_id_by_namespace_and_key(shop_name, access_token, namespace, key, owner_type='PRODUCT'):
    return ShopifyGraphqlClient(shop_name, access_token).metafield_id_by_namespace_and_key(namespace, key, owner_type)

def update_product_description_and_size_table_html_metafields(shop_name, access_token, product_id, desc, html_text):
    # DEPRECATED use update_product_description_metafield and update_size_table_html_metafield instead
    query = """
    mutation updateProductMetafield($productSet: ProductSetInput!) {
        productSet(synchronous:true, input: $productSet) {
          product {
            id
            metafields (first:10) {
              nodes {
                id
                namespace
                key
                value
              }
            }
          }
          userErrors {
            field
            code
            message
          }
        }
    }
    """

    if product_id.isnumeric():
        product_id = f'gid://shopify/Product/{product_id}'
    product_description_mf_id = metafield_id_by_namespace_and_key(shop_name, access_token, 'custom', 'product_description')
    size_table_html_mf_id = metafield_id_by_namespace_and_key(shop_name, access_token, 'custom', 'size_table_html')
    variables = {
      "productSet": {
        "id": product_id,
        "metafields": [
          {
            "id": product_description_mf_id,
            "namespace": "custom",
            "key": "product_description",
            "type": "rich_text_field",
            "value": json.dumps(desc)
          },
          {
            "id": size_table_html_mf_id,
            "namespace": "custom",
            "key": "size_table_html",
            "type": "multi_line_text_field",
            "value": html_text
          }
        ]
      }
    }

    res = run_query(shop_name, access_token, query, variables)
    if res['productSet']['userErrors']:
        raise RuntimeError(f"Failed to update the metafield: {res['productSet']['userErrors']}")
    return res

def old_update_product_description_metafield(shop_name, access_token, product_id, desc):
    # DEPRECATED use update_product_description_metafield
    query = """
    mutation updateProductMetafield($productSet: ProductSetInput!) {
        productSet(synchronous:true, input: $productSet) {
          product {
            id
            metafields (first:10) {
              nodes {
                id
                namespace
                key
                value
              }
            }
          }
          userErrors {
            field
            code
            message
          }
        }
    }
    """

    if product_id.isnumeric():
        product_id = f'gid://shopify/Product/{product_id}'
    metafield_id = metafield_id_by_namespace_and_key(shop_name, access_token, 'custom', 'product_description')
    variables = {
      "productSet": {
        "id": product_id,
        "metafields": [
          {
            "id": metafield_id,
            "namespace": "custom",
            "key": "product_description",
            "type": "rich_text_field",
            "value": json.dumps(desc)
          }
        ]
      }
    }

    res = run_query(shop_name, access_token, query, variables)
    if res['productSet']['userErrors']:
        raise RuntimeError(f"Failed to update the metafield: {res['productSet']['userErrors']}")
    return res


def old_update_size_table_html_metafield(shop_name, access_token, product_id, html_text):
    # DEPRECATED use update_size_table_html_metafield
    query = """
    mutation updateProductMetafield($productSet: ProductSetInput!) {
        productSet(synchronous:true, input: $productSet) {
          product {
            id
            metafields (first:10) {
              nodes {
                id
                namespace
                key
                value
              }
            }
          }
          userErrors {
            field
            code
            message
          }
        }
    }
    """

    if product_id.isnumeric():
        product_id = f'gid://shopify/Product/{product_id}'
    variables = {
      "productSet": {
        "id": product_id,
        "metafields": [
          {
            "id": metafield_id_by_namespace_and_key(shop_name, access_token, 'custom', 'size_table_html'),
            "namespace": "custom",
            "key": "size_table_html",
            "type": "multi_line_text_field",
            "value": html_text
          }
        ]
      }
    }

    res = run_query(shop_name, access_token, query, variables)
    if res['productSet']['userErrors']:
        raise RuntimeError(f"Failed to update the metafield: {res['productSet']['userErrors']}")
    return res


def product_description_by_product_id(shop_name, access_token, product_id):
    return ShopifyGraphqlClient(shop_name, access_token).product_description_by_product_id(product_id)

def product_by_query(shop_name, access_token, query_string):
    return ShopifyGraphqlClient(shop_name, access_token).product_by_query(query_string)

def product_by_title(shop_name, access_token, title):
    return product_by_query(shop_name, access_token, f"title:'{title}'")

def product_id_by_title(shop_name, access_token, title):
    return product_by_title(shop_name, access_token, title)['id']

def product_by_handle(shop_name, access_token, handle):
    return product_by_query(shop_name, access_token, f"handle:'{handle}'")

def product_id_by_handle(shop_name, access_token, handle):
    return product_by_handle(shop_name, access_token, handle)['id']

def medias_by_product_id(shop_name, access_token, product_id):
    return ShopifyGraphqlClient(shop_name, access_token).medias_by_product_id(product_id)

def product_variants_by_product_id(shop_name, access_token, product_id):
    return ShopifyGraphqlClient(shop_name, access_token).product_variants_by_product_id(product_id)

def product_id_by_variant_id(shop_name, access_token, variant_id):
    return ShopifyGraphqlClient(shop_name, access_token).product_id_by_variant_id(variant_id)

def remove_product_media_by_product_id(shop_name, access_token, product_id, media_ids=None):
    return ShopifyGraphqlClient(shop_name, access_token).remove_product_media_by_product_id(product_id, media_ids)

def assign_images_to_product(shop_name, access_token, resource_urls, alts, product_id):
    return ShopifyGraphqlClient(shop_name, access_token).assign_images_to_product(resource_urls, alts, product_id)

def check_rohseoul_media(sku, medias):
    if medias:
      filename = medias[0]['image']['url'].rsplit('/', 1)[-1]
      return f'{sku}_0' in filename or filename.startswith('b1_') or '_0_' in filename
    logger.info(f'no media for {sku}')
    return True

def medias_by_variant_id(shop_name, access_token, variant_id):
    return ShopifyGraphqlClient(shop_name, access_token).medias_by_variant_id(variant_id)

def medias_by_sku(shop_name, access_token, sku):
    return ShopifyGraphqlClient(shop_name, access_token).medias_by_sku(sku)

def variant_by_sku(shop_name, access_token, sku):
    return ShopifyGraphqlClient(shop_name, access_token).variant_by_sku(sku)

def product_id_by_sku(shop_name, access_token, sku):
    return ShopifyGraphqlClient(shop_name, access_token).product_id_by_sku(sku)

def variant_by_variant_id(shop_name, access_token, variant_id):
    return ShopifyGraphqlClient(shop_name, access_token).variant_by_variant_id(variant_id)

def variant_id_by_sku(shop_name, access_token, sku):
    return ShopifyGraphqlClient(shop_name, access_token).variant_id_by_sku(sku)

def generate_staged_upload_targets(shop_name, access_token, file_names, mime_types):
    return ShopifyGraphqlClient(shop_name, access_token).generate_staged_upload_targets(file_names, mime_types)

def detach_variant_media(shop_name, access_token, product_id, variant_id, media_id):
    return ShopifyGraphqlClient(shop_name, access_token).detach_variant_media(product_id, variant_id, media_id)

def product_media_by_file_name(shop_name, access_token, product_id, name):
    return ShopifyGraphqlClient(shop_name, access_token).media_by_product_id_by_file_name(product_id, name)

def assign_image_to_skus(shop_name, access_token, product_id, media_id, variant_ids):
    return ShopifyGraphqlClient(shop_name, access_token).assign_image_to_skus(product_id, media_id, variant_ids)

def location_id_by_name(shop_name, access_token, name):
    return ShopifyGraphqlClient(shop_name, access_token).location_id_by_name(name)

def inventory_item_id_by_sku(shop_name, access_token, sku):
    return ShopifyGraphqlClient(shop_name, access_token).inventory_item_id_by_sku(sku)

def set_inventory_quantity_by_sku_and_location_id(shop_name, access_token, sku, location_id, quantity):
    return ShopifyGraphqlClient(shop_name, access_token).set_inventory_quantity_by_sku_and_location_id(sku, location_id, quantity)

def run_query(shop_name, access_token, query, variables=None):
    return ShopifyGraphqlClient(shop_name, access_token).run_query(query, variables)


def main():
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)
    print(os.getenv('ACCESS_TOKEN'))
    dirname = r'/Users/taro/Downloads/jpg追加/'
    local_paths = [f'{dirname}{p}' for p in os.listdir(dirname) if 'product_detail_' in p]
    replace_image_files('apricot-studios', os.getenv('ACCESS_TOKEN'), local_paths)


if __name__ == '__main__':
    main()
