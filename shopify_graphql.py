import json
import os
import pprint
from string import punctuation

import shopify
from dotenv import load_dotenv
from graphql_queries import query_epokhe_products, query_mutate_product

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


def main():
    activate_shopify_session()
    response_text = shopify.GraphQL().execute(query_epokhe_products)

    result = json.loads(response_text)
    pprint.pprint(result['data']['products']['nodes'][0])

    def str_to_parts(s):
        return list(filter(None, map(str.strip, s.lower().translate(str.maketrans({c: '' for c in punctuation})).split(' '))))

    for product in result['data']['products']['nodes']:
        title = product['title']
        variant_title = product['variants']['nodes'][0]['title']    # only one variant for each EPOKHE products
        parts = str_to_parts(title)
        parts += str_to_parts(variant_title)
        new_handle = '-'.join(parts)
        seo_title = ' | '.join([title, variant_title])
        print(product['id'])
        print(title)
        print(variant_title)
        print(new_handle)
        print(seo_title)
        print()
        print(f'updating {title} - {variant_title}')
        res = mutate_product(product['id'], seo_title, new_handle)
        pprint.pprint(json.loads(res))


if __name__ == '__main__':
    main()
