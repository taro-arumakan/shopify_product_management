from alvana.product_create import product_info_list_from_sheet, process_product_images
import logging
logging.basicConfig(level=logging.INFO)

def main():
    titles = ['SUMMER WOOL FR TEE SHIRTS',
              'SUMMER WOOL L/S TEE SHIRTS']
    from utils import client
    import pprint
    c = client('alvanas')
    product_info_list = product_info_list_from_sheet(c, c.sheet_id, 'Product Master')
    ress = []
    for product_info in product_info_list:
        if product_info['title'] in titles:
            print(f'processing {product_info["title"]}')
            ress.append(c.process_product_images(product_info,
                                                 local_dir='/Users/taro/Downloads/alvana20250418/',
                                                 local_prefix='upload_20250418_'))
    pprint.pprint(ress)


if __name__ == '__main__':
    main()
