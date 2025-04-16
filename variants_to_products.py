import os
from shopify_product_management import shopify_utils
from dotenv import load_dotenv

def main():
    load_dotenv(override=True)
    shop_name = 'kumej'
    access_token = os.getenv('ACCESS_TOKEN')

    product_title = 'Hooded Quilted Goose Down Jumper'
    shopify_utils.product_variants_to_products(shop_name, access_token, product_title)


if __name__ == '__main__':
    main()
