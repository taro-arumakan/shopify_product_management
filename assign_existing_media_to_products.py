import utils

def main():
    import logging
    logging.basicConfig(level=logging.INFO)

    c = utils.client('gbhjapan')
    bundled = c.product_by_title('STAINLESS STEEL TUMBER & POUCH')
    sourced1 = c.product_by_title('STAINLESS STEEL TUMBLER')
    sourced2 = c.product_by_title('TUMBLER POUCH')

    product_ids = [bundled['id']]
    media_ids = list(reversed([m['id'] for m in sourced2['media']['nodes']]))
    media_ids += list(reversed([m['id'] for m in sourced1['media']['nodes']]))
    for media_id in media_ids:
        c.assign_existing_image_to_products_by_id(media_id, product_ids)

if __name__ == '__main__':
    main()
