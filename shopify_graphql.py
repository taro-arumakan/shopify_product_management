import json
import os
import pprint

import shopify
from dotenv import load_dotenv
from graphql_queries import query_epokhe_products, query_mutate_product, query_update_variant_title

def activate_shopify_session():
    shop_url = "what-youth-japan.myshopify.com"
    api_version = '2024-01'

    load_dotenv()   # API_KEY, API_SECRET, ACCESS_TOKEN
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    session = shopify.Session(shop_url, api_version, ACCESS_TOKEN)
    shopify.ShopifyResource.activate_session(session)


def mutate_product(product_id: str, seo_title: str, url_handle: str) -> str:
    variables = dict(id=product_id, seo_title=seo_title, url_handle=url_handle)
    response_text = shopify.GraphQL().execute(query_mutate_product, variables=variables)
    return response_text


def update_variant_title(variant_id: str, title: str) -> str:
    variables = dict(id=variant_id, new_title=title)
    response_text = shopify.GraphQL().execute(query_update_variant_title, variables=variables)
    return response_text


def shorten_variant_title(variant_title):
    parts = variant_title.split(' ')
    return ''.join(p[0] for p in parts)


def main():
    activate_shopify_session()
    response_text = shopify.GraphQL().execute(query_epokhe_products)

    result = json.loads(response_text)
    pprint.pprint(result['data']['products']['nodes'][0])

    for product in result['data']['products']['nodes']:
        title = product['title']
        # only one variant for each EPOKHE products
        variant_id = product['variants']['nodes'][0]['id']
        variant_title = product['variants']['nodes'][0]['title']
        new_variant_title = variant_title.title()

        if variant_title != new_variant_title:
            print(f'Updating {title} {variant_title} at {variant_id}')
            print(f'  {variant_title} --> {new_variant_title}')
            print()
            res = update_variant_title(variant_id, new_variant_title)
            pprint.pprint(json.loads(res))


if __name__ == '__main__':
    main()
