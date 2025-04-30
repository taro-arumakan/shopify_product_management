import logging
import utils
import pprint

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
        'Halter Layering Tencel Sweater',
    ]
    client = utils.client('kumej')
    for product_title in titles:
        print(product_title)
        products = client.products_by_title(product_title, additional_fields=['createdAt'])
        product = sorted(products, key=lambda p: p['createdAt'])[0]
        assert product['variants']['nodes'][0]['selectedOptions'][0]['name'] == 'カラー'
        variant_ids = [v['id'] for v in product['variants']['nodes']]
        tfs = [False] * len(variant_ids)
        client.update_variant_inventory_track_by_variant_id(product_id=product['id'], variant_ids=variant_ids, inventory_track_tfs=tfs)


if __name__ == '__main__':
    main()
