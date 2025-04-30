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
    ]
    client = utils.client('kumej')
    for product_title in titles:
        print(product_title)
        products = client.products_by_title(product_title, additional_fields=['createdAt'])
        product = sorted(products, key=lambda p: p['createdAt'])[0]
        assert product['variants']['nodes'][0]['selectedOptions'][0]['name'] == 'カラー'
        variant_ids, skus = zip(*((v['id'], f"archived_{v['sku']}") for v in product['variants']['nodes']))
        print(variant_ids)
        print(skus)
        client.update_variant_sku_by_variant_id(product_id=product['id'], variant_ids=variant_ids, skus=skus)


if __name__ == '__main__':
    main()
