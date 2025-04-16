import shopify_graphql_client
tags_mapping = {
    '2024 BF 10% OFF APPAREL': '2024 BF 10% OFF APPAREL',
    '2024 BF 10% OFF COSMETICS': '2024 BF 10% OFF COSMETICS',
    '2024 BF 20% OFF APPAREL': '2024 BF 20% OFF APPAREL',
    '2024 BF 5% OFF APPAREL': '2024 BF 5% OFF APPAREL',
    '2024 Holiday 10% OFF HOME': '2024 Holiday 10% OFF HOME',
    '2024 Holiday 15% OFF APPAREL': '2024 Holiday 15% OFF APPAREL',
    '2024 Holiday 15% OFF COSMETICS': '2024 Holiday 15% OFF COSMETICS',
    '2024 Holiday 15% OFF HOME': '2024 Holiday 15% OFF HOME',
    '2024 Holiday 25% OFF COSMETICS': '2024 Holiday 25% OFF COSMETICS',
    '2024 Holiday 30% OFF APPAREL': '2024 Holiday 30% OFF APPAREL',
    '2024 Holiday 5% OFF HOME': '2024 Holiday 5% OFF HOME',
    '2024-11-08': '2024-11-08',
    '2024-11-21': '2024-11-21',
    '2025-01-31': '2025-01-31',
    '2025-03-03': '2025-03-03',
    '2025-03-17': '2025-03-17',
    '24 WINTER': '24 WINTER',
    '24FALL': '24FALL',
    '24SP': '24SP',
    '24SU': '24SU',
    '25 CAPSULE COLLECTION': '25 CAPSULE COLLECTION',
    '25 SPRING': '25 SPRING',
    'APPAREL': 'APPAREL',
    'BAG&POUCH': 'BAG&POUCH',
    'BATHROOM': 'BATHROOM',
    'BODY CARE': 'BODY CARE',
    'BOTTOM': 'Bottoms',
    'Bottom': 'Bottoms',
    'CLEANING': 'CLEANING',
    'COSMETICS': 'COSMETICS',
    'DRESS': 'Dress',
    'Dress': 'Dress',
    'ETC': 'ETC',
    'GIFT SET': 'GIFT SET',
    'HAIR CARE': 'HAIR CARE',
    'HAIR&BODY': 'HAIR&BODY',
    'HOME': 'HOME',
    'KITCHEN': 'KITCHEN',
    'MAKE UP': 'MAKE UP',
    'OUTER': 'Outer',
    'Outer': 'Outer',
    'SKIN CARE': 'SKIN CARE',
    'STATIONERY': 'STATIONERY',
    'TOOL': 'TOOL',
    'TOP': 'Tops',
    'Top': 'Tops',
    'Tops': 'Tops',
    'best': 'best',
    'new': 'new',
    'new2025-01-31': 'new2025-01-31',
}
def get_tag(tag):
    if tag in tags_mapping:
        return tags_mapping[tag]
    else:
        assert tag in tags_mapping.values(), "Tag not found in mapping"
        return tag
def main():
    sgc = shopify_graphql_client.get('gbhjapan')
    for b, a in tags_mapping.items():
        if b != a:
            print(f'processing {b}')
            products = sgc.products_by_tag(b)
            for product in products:
                tags = product['tags']
                new_tags = [get_tag(tag) for tag in tags]
                if tags != new_tags:
                    print(f'Updating {product["title"]}')
                    print(f'from {tags}')
                    print(f'to {new_tags}')
                    sgc.update_product_tags(product['id'], ','.join(new_tags))

if __name__ == '__main__':
    main()
