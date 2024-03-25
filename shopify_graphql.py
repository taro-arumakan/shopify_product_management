import json
import os
import pprint
from slugify import slugify

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


def main():
    activate_shopify_session()
    response_text = shopify.GraphQL().execute(query_epokhe_products)

    result = json.loads(response_text)

    for product in result['data']['products']['nodes']:
        title = product['title']
        # only one variant for each EPOKHE products
        variant_title = product['variants']['nodes'][0]['title']
        new_title = title_with_shortened_variant_title(title, variant_title)
        new_slug = slug_for(new_title, variant_title)
        new_seo_title = f'{new_title} - {variant_title}'

        print(f'{product['id']}')
        print(f'{title} {variant_title} to {new_title}')
        print(f'new slug is {new_slug}')
        print(f'new seo title is {new_seo_title}')
        mutate_product(product['id'], new_title, new_seo_title, new_slug)
        print()


if __name__ == '__main__':
    main()
