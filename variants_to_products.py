import logging
import utils


def main():
    logging.basicConfig(level=logging.INFO)
    titles = [
        'Cropped Organza Collar Blouson Jacket',
        'Fitted Button Knitted Vest',
        'Organza Layered Midi Skirt',
        'Fringe Long Sleeve Cardigan',
        'Tweed Short Sleeve Blouse',
        '[Women] Wrinkle Free Over-Fit Shirt',
        'Pleated Ruffle Sleeveless Long Dress',
    ]
    client = utils.client('kumej')
    for product_title in titles:
        client.product_variants_to_products(product_title)


if __name__ == '__main__':
    main()
