import utils

def main():
    client = utils.client('kumej')
    names = [
        'Basic Sliket Sweater',
        'Fringe Long Sleeve Cardigan',
        'Fringe Waist H-Line Skirt',
        'Off-the-Shoulder Shirt Blouse',
        'Organza Layered Midi Skirt',
        'Pleated Ruffle Sleeveless Long Dress',
        'Organza Back Mini Dress',
        'Side Frayed Wide Denim Pants',
        'Linen Boat-neck Vest',
        'Organza V-neck Trench Coat',
        'Back String Cotton Nylon Summer Jacket',
        'Twisted Back Detail T-shirt',
        'H-line Knitted Skirt ',
        'ESSENTIAL Basic Tank Top ',
        'ESSENTIAL Semi-Cropped Cotton T-shirt',
        'Pintucked Layering Dress',
        'Cropped Organza Collar Blouson Jacket',
        'Fitted Button Knitted Vest',
        'Back Buckle Detail Semi Bootcut Denim Pants',
        'Semi Wide Work Denim Pants',
        'Striped knitted Halter Top',
        'Cropped Linen Ribbon Tie Top',
        'One Button Square-neck Jacket',
        'Fringe Detail Oversized Shirt',
        'Ribbon Boxer Shorts ',
        'Tweed Short Sleeve Blouse',
        'Lace Embroiered Puff Sleeves Blouse',
        'Halter Layering Tencel Sweater',
    ]
    c = utils.client('kumej')
    collection = c.collection_by_title('HANKYU UMEDA COLLECTION')
    collection_id = collection['id']
    existing_product_ids = [p['id'] for p in collection['products']['nodes']]
    product_ids = sum([client.product_ids_by_title(name.replace('ESSENTIAL ', '')) for name in names], [])
    new_product_ids = [pi for pi in product_ids if pi not in existing_product_ids]
    c.collection_add_products(collection_id, new_product_ids)


if __name__ == '__main__':
    main()
