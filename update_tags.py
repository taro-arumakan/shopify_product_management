import utils
tags_map = {
    'standard': 'Standard Line',
    }

def main():
    sgc = utils.client('archive-epke')
    for a, b in tags_map.items():
        products = sgc.products_by_tag(a)
        for product in products:
            tags = product['tags']
            new_tags = [tags_map.get(t, t) for t in tags]
            if tags != new_tags:
                print(f'Updating {product["title"]}')
                print(f'from {tags}')
                print(f'to {new_tags}')
                sgc.update_product_tags(product['id'], ','.join(new_tags))

if __name__ == '__main__':
    main()
