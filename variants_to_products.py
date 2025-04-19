import utils

def main():
    client = utils.client('kumej')
    product_title = 'Hooded Quilted Goose Down Jumper'
    client.product_variants_to_products(product_title)


if __name__ == '__main__':
    main()
