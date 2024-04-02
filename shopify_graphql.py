import json
import os
import pprint
from slugify import slugify

import shopify
from dotenv import load_dotenv
from graphql_queries import query_epokhe_products, query_mutate_product, query_update_variant_title, query_epokhe_variants_by_product_query, query_update_variant_sku

def activate_shopify_session():
    shop_url = "what-youth-japan.myshopify.com"
    api_version = '2024-01'

    load_dotenv()   # API_KEY, API_SECRET, ACCESS_TOKEN
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    session = shopify.Session(shop_url, api_version, ACCESS_TOKEN)
    shopify.ShopifyResource.activate_session(session)


def epokhe_products():
    response_text = shopify.GraphQL().execute(query_epokhe_products)
    results = json.loads(response_text)
    products_data = [dict(product_id=r['id'],
                          product_title=r['title'],
                          variant_id=r['variants']['nodes'][0]['id'],
                          variant_title=r['variants']['nodes'][0]['title'],
                          sku=r['variants']['nodes'][0]['sku'])
                          for r in results['data']['products']['nodes']]
    return products_data


def mutate_product(product_id: str, title: str|None=None,
                                    seo_title: str|None=None,
                                    url_handle: str|None=None) -> str:
    variables = dict(id=product_id, title=title, seo_title=seo_title, url_handle=url_handle)
    if title:
        variables['title'] = title
    if seo_title:
        variables['seo_title'] = seo_title
    if url_handle:
        variables['url_handle'] = url_handle
    response_text = shopify.GraphQL().execute(query_mutate_product, variables=variables)
    return response_text


def update_variant_title(variant_id: str, title: str) -> str:
    variables = dict(id=variant_id, new_title=title)
    response_text = shopify.GraphQL().execute(query_update_variant_title, variables=variables)
    return response_text


def shorten_variant_title(variant_title):
    parts = variant_title.split(' ')
    return ''.join(p[0] for p in parts)


def title_with_shortened_variant_title(title: str, variant_title: str) -> str:
    short_variant_title = shorten_variant_title(variant_title)
    if title.endswith(short_variant_title):
        return title
    return f'{title} {short_variant_title}'


def title_without_shortened_variant_title(title: str, variant_title: str) -> str:
    short_variant_title = shorten_variant_title(variant_title)
    return title.replace(short_variant_title, '').strip()


def slug_for(title, variant_title):
    return slugify(' '.join([title_without_shortened_variant_title(title, variant_title), variant_title]))


def variant_id_and_sku_by_title(product_title: str, variant_title: str):
    variables = dict(query_string=f'vendor:EPOKHE title:{product_title}*')
    response_text = shopify.GraphQL().execute(
        query_epokhe_variants_by_product_query, variables=variables)
    for product in json.loads(response_text)['data']['products']['nodes']:
        if product['variants']['nodes'][0]['title'] == variant_title:
            return (product['variants']['nodes'][0]['id'], product['variants']['nodes'][0]['sku'])
    return (None, None)


def update_variant_sku(variant_id: str, sku: str):
    variables = dict(id=variant_id, sku=sku)
    response_text = shopify.GraphQL().execute(query_update_variant_sku, variables=variables)
    return response_text


def main():
    activate_shopify_session()
    for product in epokhe_products():
        if not product['sku']:
            print(product['product_title'], product['variant_title'])


if __name__ == '__main__':
    main()
