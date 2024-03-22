# import binascii
# import os
import json
import os
from string import punctuation

import pprint

import shopify
from dotenv import load_dotenv


def activate_shopify_session():
    shop_url = "what-youth-japan.myshopify.com"
    api_version = '2024-01'

    # shopify.Session.setup(api_key=API_KEY, secret=API_SECRET)
    # state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    # redirect_uri = "http://myapp.com/auth/shopify/callback"
    # scopes = ['read_products', 'read_orders']

    # newSession = shopify.Session(shop_url, api_version)
    # auth_url = newSession.create_permission_url(scopes, redirect_uri, state)

    # session = shopify.Session(shop_url, api_version)
    # access_token = session.request_token(request_params) # request_token will validate hmac and timing attacks
    # # you should save the access token now for future use.

    load_dotenv()   # API_KEY, API_SECRET, ACCESS_TOKEN
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    session = shopify.Session(shop_url, api_version, ACCESS_TOKEN)
    shopify.ShopifyResource.activate_session(session)

    shop = shopify.Shop.current()  # Get the current shop
    print(shop)

    # execute a graphQL call
    shop_response = shopify.GraphQL().execute("{ shop { name id } }")
    print(shop_response)

def main():
    activate_shopify_session()
    response_text = shopify.GraphQL().execute('''
    {
    products(first: 100, query: "vendor:EPOKHE") {
        nodes {
        id
        title
        variants(first: 15) {
            nodes {
            id
            title
            }
        }
        handle
        seo {
            title
        }
        }
    }
    }
    ''')


    result = json.loads(response_text)
    pprint.pprint(result['data']['products']['nodes'][0])


    def str_to_parts(s):
        return list(filter(None, map(str.strip, s.lower().translate(str.maketrans({c: '' for c in punctuation})).split(' '))))


    for product in result['data']['products']['nodes']:
        title = new_title = product['title']
        handle = product['handle']
        # only one variant for each EPOKHE products
        variant_title = product['variants']['nodes'][0]['title']
        if variant_title.upper() in title.upper():
            is_upper = title.isupper()
            new_title = title.upper().replace(
                variant_title.upper(), '').replace('-', '').strip()
            if not is_upper:
                new_title = new_title.title()
            print(title, new_title)
        parts = str_to_parts(new_title)
        parts += str_to_parts(variant_title)
        new_handle = '-'.join(parts)
        seo_title = ' | '.join([new_title, variant_title])
        print(product['id'])
        print(title)
        print(variant_title)
        print(new_title)
        print(new_handle)
        print(seo_title)
        print()
