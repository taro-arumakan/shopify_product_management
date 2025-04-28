import utils

remove_tags = ['new']

def main():
    sgc = utils.client('gbhjapan')
    for tag in remove_tags:
        print(f'processing {tag}')
        products = sgc.products_by_query(f"tag:'{tag}' AND created_at:<'2024-10-31T23:59:00+09:00'")
        for product in products:
            tags = product['tags']
            new_tags = [t for t in tags if t not in remove_tags]
            if tags != new_tags:
                print(f'Updating {product["title"]}')
                print(f'from {tags}')
                print(f'to {new_tags}')
                sgc.update_product_tags(product['id'], ','.join(new_tags))

if __name__ == '__main__':
    main()
